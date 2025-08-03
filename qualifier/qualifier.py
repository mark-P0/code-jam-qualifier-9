import typing
from dataclasses import dataclass
from enum import Enum


class RequestType(Enum):
    STAFF_ON_DUTY = "staff.onduty"
    STAFF_OFF_DUTY = "staff.offduty"
    ORDER = "order"


@dataclass(frozen=True)
class Request:
    scope: typing.Mapping[str, typing.Any]

    receive: typing.Callable[[], typing.Awaitable[object]]
    send: typing.Callable[[object], typing.Awaitable[None]]


class RestaurantManager:
    def __init__(self):
        """Instantiate the restaurant manager.

        This is called at the start of each day before any staff get on
        duty or any orders come in. You should do any setup necessary
        to get the system working before the day starts here; we have
        already defined a staff dictionary.
        """
        self.staff = {}

    def __get_staff_with_speciality(self, speciality):
        for _, staff_request in self.staff.items():
            staff_specialities = staff_request.scope.get("speciality")

            if speciality in staff_specialities:
                return staff_request

        return None

    async def __call__(self, request: Request):
        """Handle a request received.

        This is called for each request received by your application.
        In here is where most of the code for your system should go.

        :param request: request object
            Request object containing information about the sent
            request to your application.
        """
        ...

        request_type = request.scope.get("type")
        request_id = request.scope.get("id")

        if request_type == RequestType.STAFF_ON_DUTY.value:
            self.staff[request_id] = request

        if request_type == RequestType.STAFF_OFF_DUTY.value:
            self.staff.pop(request_id, None)

        if request_type == RequestType.ORDER.value:
            request_speciality = request.scope.get("speciality")
            staff = self.__get_staff_with_speciality(request_speciality)

            if staff is None:
                raise ValueError(f"No staff can handle request: {request}")

            order = await request.receive()
            await staff.send(order)

            order_result = await staff.receive()
            await request.send(order_result)
