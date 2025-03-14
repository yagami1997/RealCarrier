from setuptools import setup, find_packages

# 最后更新时间（PST）: 2025-03-05 21:31:39

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="realcarrier",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="美国电话号码查询工具 - 支持多API接口 (Telnyx & Twilio)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/realcarrier",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Telecommunications Industry",
        "Topic :: Communications :: Telephony",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.25.0",
        "rich>=10.0.0",
        "pandas>=1.3.0",
        "pydantic>=1.8.0",
        "keyring>=23.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.1.0",
            "flake8>=4.0.0",
            "mypy>=0.931",
            "coverage>=6.3.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "lnp=lnptool.cli:cli",
        ],
    },
)
