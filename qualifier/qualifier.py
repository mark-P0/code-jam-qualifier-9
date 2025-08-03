import typing
from dataclasses import dataclass
from enum import Enum


class RequestType(Enum):
    STAFF_ON_DUTY = "staff.onduty"
    STAFF_OFF_DUTY = "staff.offduty"
    ORDER = "order"

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if value == member.value:
                return member

        return None


@dataclass(frozen=True)
class Request:
    scope: typing.Mapping[str, typing.Any]

    receive: typing.Callable[[], typing.Awaitable[object]]
    send: typing.Callable[[object], typing.Awaitable[None]]

    @property
    def type(self):
        request_type_raw = self.scope.get("type")
        request_type = RequestType.from_value(request_type_raw)

        return request_type

    @property
    def id(self):
        request_id = self.scope.get("id")

        return request_id

    @property
    def speciality(self):
        request_speciality = self.scope.get("speciality")

        return request_speciality


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
            if staff.id is None:
                raise ValueError("Some staff does not have an ID")

            yield (staff.id, staff)

    def __getitem__(self, key):
        for staff in self.staff:
            if key == staff.id:
                return staff


class RestaurantStaff(RestaurantStaffClass):
    def add(self, staff_request: Request):
        if staff_request.type != RequestType.STAFF_ON_DUTY:
            raise ValueError("Cannot add staff with invalid request type")

        self.staff.append(staff_request)

    def remove(self, staff_request: Request):
        if staff_request.type != RequestType.STAFF_OFF_DUTY:
            raise ValueError("Cannot remove staff with invalid request type")

        self.staff = [staff for staff in self.staff if staff.id != staff_request.id]

    def get_specialized(self, request: Request):
        for staff in self.staff:
            staff_specialities = staff.speciality or []
            if request.speciality in staff_specialities:
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

        if request.type == RequestType.STAFF_ON_DUTY:
            self.__staff.add(request)

        if request.type == RequestType.STAFF_OFF_DUTY:
            self.__staff.remove(request)

        if request.type == RequestType.ORDER:
            staff = self.__staff.get_specialized(request)

            if staff is None:
                raise ValueError(f"No staff can handle request: {request}")

            order = await request.receive()
            await staff.send(order)

            order_result = await staff.receive()
            await request.send(order_result)


if __name__ == "__main__":
    ...
