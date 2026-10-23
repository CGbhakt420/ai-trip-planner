from setuptools import find_packages,setup
from typing import List

def get_requirements()->List[str]:
    requirement_list:List[str]=[]
    
    try:
        with open("requirements.txt") as requirement_file:
            requirement_list=requirement_file.readlines()
            for i in range(len(requirement_list)):
                requirement_list[i]=requirement_list[i].strip()
    except Exception as e:
        print(f"Error occurred while reading requirements.txt: {e}")

    return requirement_list

print(get_requirements())

setup(
    name="ai-trip-planner",
    version="0.0.1",
    author="Sanchit",
    author_email="sanchit.kr007@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements()
)