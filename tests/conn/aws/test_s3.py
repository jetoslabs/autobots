import time

import pytest

from src.autobots.conn.aws.s3 import get_s3
from src.autobots.core.utils import gen_hash


@pytest.mark.asyncio
async def test_aws_s3_happy_path(set_test_settings):
    str1 = "Delhi,officially the National Capital Territory (NCT) of Delhi, is a city and a union territory of India containing New Delhi, the capital of India. Straddling the Yamuna river, primarily its western or right bank, Delhi shares borders with the state of Uttar Pradesh in the east and with the state of Haryana in the remaining directions. The NCT covers an area of 1,484 square kilometres (573 sq mi). According to the 2011 census, Delhi's city proper population was over 11 million, while the NCT's population was about 16.8 million. Delhi's urban agglomeration, which includes the satellite cities Ghaziabad, Faridabad, Gurgaon and Noida in an area known as the National Capital Region (NCR), has an estimated population of over 28 million, making it the largest metropolitan area in India and the second-largest in the world"
    str1_id = gen_hash(str1)

    # put data in s3
    res1 = await get_s3().put(data=str1, filename=gen_hash(str1))
    assert res1 == len(str1)

    # get data from file
    res1_data = await get_s3().get(filename=gen_hash(str1))
    assert res1_data == str1

    # delete file from s3
    del_res1 = await get_s3().delete(filename=str1_id)
    assert del_res1[0].get("Key") == gen_hash(str1)


@pytest.mark.asyncio
async def test_aws_s3_list(set_test_settings):
    prefix = "test_aws_s3_list"
    data = "testdata"
    num_of_files = 5
    try:
        # put objects
        for i in range(num_of_files):
            await get_s3().put(data, f"{prefix}/{data}_{i}")

        time.sleep(3)
        # list objects
        s3_objects = await get_s3().list(prefix)
        assert len(s3_objects) == num_of_files

    finally:

        # Delete list of objects
        await get_s3().delete_prefix(prefix)

        time.sleep(3)

        s3_objects = await get_s3().list(prefix)
        assert len(s3_objects) == 0
