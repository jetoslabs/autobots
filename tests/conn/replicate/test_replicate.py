import pytest

from src.autobots.conn.replicate.replicate import get_replicate


@pytest.mark.asyncio
async def test_list_collections_happy_path(set_test_settings):
    collections = await get_replicate().list_collections_namespace()
    assert collections


@pytest.mark.asyncio
async def test_list_models_happy_path(set_test_settings):
    models = await get_replicate().list_models()
    assert models


# @pytest.mark.asyncio
# async def test_face_swap_happy_path(set_test_settings):
#     params = YanOpsFaceSwapParams(
#         target_image="https://replicate.delivery/pbxt/JkUYWp60oNwz1SF9AJvJPv7upLqucTyaeCxQ07qZGijlDKxt/face_swap_09.jpg",
#         source_image="https://media.licdn.com/dms/image/D4E03AQFsm5Y9vP66Cw/profile-displayphoto-shrink_200_200/0/1698898979044?e=2147483647&v=beta&t=_JUeBPwHfyfbcuEtp9vSfuF3r9gWARAMIKe3FQCTp6k"
#     )
#     output = await get_replicate().yan_ops_face_swap.run(params)
#     assert output
#     assert output.code == 200
