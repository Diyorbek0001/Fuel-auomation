from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.integrations.samsara import SamsaraClient, SamsaraVehicleSnapshot
from app.models import Driver, SamsaraSyncLog, SamsaraSyncState, Truck
from app.models.common import utcnow
from app.schemas.truck import DriverSummaryOut, TruckOut
from app.services.notification_event_engine import process_truck_update
from app.services.notification_service import create_system_notification_event
from app.services.telegram_service import send_telegram_message
from app.services.truck_broadcaster import truck_broadcaster


async def sync_all_samsara_accounts(session: AsyncSession) -> list[SamsaraSyncLog]:
    settings = get_settings()
    logs: list[SamsaraSyncLog] = []
    for account_name, api_token in settings.samsara_accounts:
        logs.append(await sync_samsara_account(session, account_name=account_name, api_token=api_token))
    return logs


async def sync_samsara_account(session: AsyncSession, *, account_name: str, api_token: str) -> SamsaraSyncLog:
    settings = get_settings()
    started_at = utcnow()
    log = SamsaraSyncLog(account_name=account_name, started_at=started_at, success=False)
    session.add(log)
    await session.flush()

    try:
        snapshots = await SamsaraClient(
            api_token,
            base_url=settings.samsara_base_url,
            group_id=settings.samsara_group_id,
        ).list_vehicle_snapshots()
        updated = 0
        for snapshot in snapshots:
            truck = await _upsert_truck(session, account_name=account_name, snapshot=snapshot)
            await process_truck_update(session, truck)
            truck_broadcaster.publish_truck(_truck_out(truck))
            updated += 1
        await _mark_sync_success(session, account_name)
        log.vehicles_read = len(snapshots)
        log.vehicles_updated = updated
        log.success = True
        log.completed_at = utcnow()
        await session.commit()
    except Exception as exc:
        await session.rollback()
        log = SamsaraSyncLog(account_name=account_name, started_at=started_at, success=False)
        session.add(log)
        log.error_message = str(exc)
        log.completed_at = utcnow()
        await _mark_sync_error(session, account_name, str(exc))
        await _create_sync_failed_notification(session, account_name, str(exc))
        await session.commit()
    return log


async def _upsert_truck(session: AsyncSession, *, account_name: str, snapshot: SamsaraVehicleSnapshot) -> Truck:
    truck = await session.scalar(
        select(Truck).where(
            Truck.samsara_account_name == account_name,
            Truck.samsara_vehicle_id == snapshot.vehicle_id,
        )
    )
    if truck is None:
        truck = Truck(
            samsara_account_name=account_name,
            samsara_vehicle_id=snapshot.vehicle_id,
            unit_number=snapshot.unit_number,
        )
        session.add(truck)

    truck.unit_number = snapshot.unit_number
    truck.previous_fuel_percent = truck.fuel_percent
    truck.previous_latitude = truck.latitude
    truck.previous_longitude = truck.longitude
    truck.fuel_percent = snapshot.fuel_percent
    truck.latitude = snapshot.latitude
    truck.longitude = snapshot.longitude
    truck.odometer_miles = snapshot.odometer_miles
    truck.speed_mph = snapshot.speed_mph
    truck.heading_degrees = snapshot.heading_degrees
    now = utcnow()
    truck.last_samsara_sync_at = now
    truck.last_samsara_update_at = snapshot.update_at or now

    if snapshot.driver_name:
        truck.driver = await _upsert_driver(session, snapshot.driver_name)

    await session.flush()

    return truck


async def _upsert_driver(session: AsyncSession, name: str) -> Driver:
    driver = await session.scalar(select(Driver).where(Driver.name == name))
    if driver is None:
        driver = Driver(name=name)
        session.add(driver)
        await session.flush()
    return driver


async def _sync_state(session: AsyncSession, account_name: str) -> SamsaraSyncState:
    feed_name = f"{account_name}:vehicle_stats"
    state = await session.scalar(select(SamsaraSyncState).where(SamsaraSyncState.feed_name == feed_name))
    if state is None:
        state = SamsaraSyncState(feed_name=feed_name)
        session.add(state)
        await session.flush()
    return state


async def _mark_sync_success(session: AsyncSession, account_name: str) -> None:
    state = await _sync_state(session, account_name)
    state.last_success_at = utcnow()
    state.last_error_at = None
    state.last_error_message = None


async def _mark_sync_error(session: AsyncSession, account_name: str, message: str) -> None:
    state = await _sync_state(session, account_name)
    state.last_error_at = utcnow()
    state.last_error_message = message


async def _create_sync_failed_notification(session: AsyncSession, account_name: str, message: str) -> None:
    title = "Samsara sync failed"
    body = f"{account_name} failed to sync: {message}"
    notification = await create_system_notification_event(
        session,
        event_type="SAMSARA_SYNC_FAILED",
        title=title,
        message=body,
        dedupe_key=f"samsara_sync_failed:{account_name}:{utcnow().date().isoformat()}",
        payload_json={"account_name": account_name, "error": message},
    )
    if notification:
        try:
            await send_telegram_message(f"{title}\nAccount: {account_name}\n{message}")
        except Exception:
            return


def _truck_out(truck: Truck) -> TruckOut:
    driver = DriverSummaryOut(id=truck.driver.id, name=truck.driver.name) if truck.driver else None
    return TruckOut(
        id=truck.id,
        unit_number=truck.unit_number,
        fuel_percent=truck.fuel_percent,
        previous_fuel_percent=truck.previous_fuel_percent,
        latitude=truck.latitude,
        longitude=truck.longitude,
        previous_latitude=truck.previous_latitude,
        previous_longitude=truck.previous_longitude,
        odometer_miles=truck.odometer_miles,
        speed_mph=truck.speed_mph,
        heading_degrees=truck.heading_degrees,
        current_city=truck.current_city,
        current_state=truck.current_state,
        destination=truck.destination,
        active=truck.active,
        last_samsara_update_at=truck.last_samsara_update_at,
        last_samsara_sync_at=truck.last_samsara_sync_at,
        samsara_account_name=truck.samsara_account_name,
        driver=driver,
    )
