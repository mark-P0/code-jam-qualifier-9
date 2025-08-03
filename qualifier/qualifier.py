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


class RestaurantStaffClass:
    """
    Allow simple dictionary conversion
    """

    def __init__(self):
        """
        Staff are represented as a Request object
        """
        self.staff: list[Request] = []

    def __iter__(self):
        for staff in self.staff:
            request_id = staff.scope.get("id")
            if request_id is None:
                raise ValueError("Some staff does not have an ID")

            yield request_id, staff

    def __getitem__(self, key):
        for staff in self.staff:
            request_id = staff.scope.get("id")

            if key == request_id:
                return staff


class RestaurantStaff(RestaurantStaffClass):
    def add(self, staff_request: Request):
        request_type = staff_request.scope.get("type")
        if request_type != RequestType.STAFF_ON_DUTY.value:
            raise ValueError("Cannot add staff with invalid request type")

        self.staff.append(staff_request)

    def remove(self, staff_request: Request):
        request_type = staff_request.scope.get("type")
        request_id = staff_request.scope.get("id")

        if request_type != RequestType.STAFF_OFF_DUTY.value:
            raise ValueError("Cannot remove staff with invalid request type")

        self.staff = [
            staff for staff in self.staff if staff.scope.get("id") != request_id
        ]

    def get_specialized(self, request: Request):
        speciality = request.scope.get("speciality")

        for staff in self.staff:
            staff_specialities = staff.scope.get("speciality", [])
            if speciality in staff_specialities:
                return staff

        return None


class RestaurantManager:
    def __init__(self):
        """Instantiate the restaurant manager.

        This is called at the start of each day before any staff get on
        duty or any orders come in. You should do any setup necessary
        to get the system working before the day starts here; we have
        already defined a staff dictionary.
        """

        self.__staff = RestaurantStaff()

    @property
    def staff(self) -> dict[str, Request]:
        staff_dict = dict(self.__staff)

        return staff_dict

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

        if request_type == RequestType.STAFF_ON_DUTY.value:
            self.__staff.add(request)

        if request_type == RequestType.STAFF_OFF_DUTY.value:
            self.__staff.remove(request)

        if request_type == RequestType.ORDER.value:
            staff = self.__staff.get_specialized(request)

            if staff is None:
                raise ValueError(f"No staff can handle request: {request}")

            order = await request.receive()
            await staff.send(order)

            order_result = await staff.receive()
            await request.send(order_result)
