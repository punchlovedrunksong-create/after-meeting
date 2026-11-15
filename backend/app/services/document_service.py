"""TXT upload validation and decoding."""

from fastapi import UploadFile

from app.core.config import settings
from app.core.errors import AppError


class DocumentService:
    async def read_txt(self, file: UploadFile) -> str:
        filename = file.filename or ""
        if not filename.lower().endswith(".txt"):
            raise AppError(
                "UNSUPPORTED_FILE_TYPE",
                "TXT 파일만 업로드할 수 있습니다.",
                "TXT 형식의 회의 텍스트 파일을 선택해 주세요.",
                status_code=415,
            )

        max_bytes = settings.max_upload_mb * 1024 * 1024
        content = await file.read(max_bytes + 1)
        if len(content) > max_bytes:
            raise AppError(
                "FILE_TOO_LARGE",
                f"파일은 {settings.max_upload_mb}MB 이하여야 합니다.",
                "파일 크기를 줄인 뒤 다시 업로드해 주세요.",
                status_code=413,
            )
        if not content:
            raise AppError(
                "EMPTY_DOCUMENT",
                "파일에 읽을 내용이 없습니다.",
                "회의 텍스트가 포함된 TXT 파일을 선택해 주세요.",
                status_code=422,
            )

        text = self._decode(content)
        if not text.strip():
            raise AppError(
                "EMPTY_DOCUMENT",
                "파일에 읽을 내용이 없습니다.",
                "회의 텍스트가 포함된 TXT 파일을 선택해 주세요.",
                status_code=422,
            )
        return text.strip()

    @staticmethod
    def _decode(content: bytes) -> str:
        for encoding in ("utf-8-sig", "utf-16", "cp949"):
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise AppError(
            "UNREADABLE_DOCUMENT",
            "TXT 파일의 문자 인코딩을 읽을 수 없습니다.",
            "UTF-8 또는 CP949 형식으로 저장한 뒤 다시 업로드해 주세요.",
            status_code=422,
        )
