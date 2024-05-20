import json

from fastapi import Body, Response, status, HTTPException, Depends
from sqlalchemy.exc import NoResultFound

from auth.jwt_token import create_access_token
from deps import get_user_service
from custom_exceptions import EmailDuplicationException, InvalidData, UserNotFoundException, \
    UsernameDuplicationException
from requests import CreateUserRequest, LoginRequest

from services.user_service import UserService

from fastapi import APIRouter

auth_router = APIRouter(
    prefix="/auth",
    tags=["Users"]
)


@auth_router.post("/login")
async def login(*, user_service: UserService = Depends(get_user_service),
                request: LoginRequest = Body()):
    try:
        user = await user_service.login(request)

        access_token = create_access_token(
            data={"sub": user.username},
        )
        return Response(status_code=status.HTTP_200_OK,
                        content=json.dumps({"access_token": access_token, "token_type": "bearer"}))
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password or username")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "message": "Something went wrong",
            "code": "INTERNAL_SERVER_ERROR",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        })


@auth_router.post("/users", response_class=Response, status_code=status.HTTP_201_CREATED)
async def create_user(*, user_service: UserService = Depends(get_user_service),
                      request: CreateUserRequest = Body()):
    try:
        await user_service.create_user(request)
        return Response(status_code=status.HTTP_201_CREATED)
    except InvalidData as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={
            "message": str(e),
            "code": "INVALID_DATA",
            "status_code": status.HTTP_400_BAD_REQUEST,
        })
    except EmailDuplicationException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={
            "message": str(e),
            "code": "EMAIL_DUPLICATION",
            "status_code": status.HTTP_409_CONFLICT,
        })
    except UsernameDuplicationException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={
            "message": str(e),
            "code": "USERNAME_DUPLICATION",
            "status_code": status.HTTP_409_CONFLICT,
        })
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "message": "Something went wrong",
            "code": "INTERNAL_SERVER_ERROR",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        })
