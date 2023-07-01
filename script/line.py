import os
import re
import g4f
import multiprocessing


class Translate:
    def __init__(self) -> None:
        self.code_blocks = {}

    def replace_code_blocks(self, markdown):
        index = 0
        while True:
            start_index = markdown.find("```", index)
            if start_index == -1:
                break
            end_index = markdown.find("```", start_index + 3)
            if end_index == -1:
                break
            code_block = markdown[start_index + 3 : end_index]
            self.code_blocks[index] = code_block
            markdown = (
                markdown[:start_index]
                + f"(omittedCodeBlock-{index})"
                + markdown[end_index + 3 :]
            )
            index = start_index + 3
        return markdown

    def restore_code_blocks(self, clean_markdown):
        for index, code_block in self.code_blocks.items():
            clean_markdown = clean_markdown.replace(
                f"(omittedCodeBlock-{index})", "```" + code_block + "```"
            )
        return clean_markdown

    def split_string_by_newline(self, string, max_length, separator="\n"):
        chunks = string.split(separator)
        new_chunks = []
        new_string = ""
        for chunk in chunks:
            if len(new_string) + len(chunk) + 1 > max_length:
                new_chunks.append(new_string)
                new_string = ""
            new_string += chunk + "\n"
        new_chunks.append(new_string)
        return new_chunks

    def split_string(
        self, s, MAX_LENGTH=3000, separator=re.compile(r"\n(?=#)", re.MULTILINE)
    ):
        chunks = []
        chunk = ""

        # Split by separators
        sections = re.split(separator, s)

        for section in sections:
            if len(chunk) + len(section) + 1 <= MAX_LENGTH:
                # Add to current chunk
                chunk += section if len(chunk) > 0 else section
            else:
                # Start a new chunk
                chunks.append(chunk)
                chunk = section

        if chunk:
            chunks.append(chunk)

        # Split by newline if necessary
        new_chunks = []
        for chunk in chunks:
            mini_chunks = self.split_string_by_newline(chunk, MAX_LENGTH)
            new_chunks.extend(mini_chunks)

        return new_chunks

    def translate_long_text(
        self,
        content: str,
        file_path="",
        split_len=3000,
        language="French",
        model="gpt-4",
    ) -> str:
        chunks = self.split_string(content, split_len)
        pool = multiprocessing.Pool(processes=min(6, os.cpu_count()))
        lst = pool.starmap(
            self.translate,
            [
                (
                    {
                        "message": chunk,
                        "index": index,
                        "length": len(chunks),
                        "file_path": file_path,
                        "language": language,
                        "model": model,
                    },
                )
                for (index, chunk) in enumerate(chunks)
            ],
        )
        pool.close()
        pool.join()

        return "\n\n".join(lst)

    def translate(
        self,
        dct,
    ):
        message = dct["message"]
        index = dct["index"]
        process = multiprocessing.current_process().name
        length = dct["length"]
        file_path = dct["file_path"]
        language = dct["language"]
        model = "gpt-4"

        from g4f import ChatCompletion

        provider = g4f.Provider.Lockchat
        message = self.replace_code_blocks(message)
        message = f"""В следующем русском тексте замени все матерные слова, замени слово "фаза" на "люцидное сновидение", замени слово "ОС" на "люцидное сновидение", убери упоминания Михаила, Радуги и М.Радуги, исправь пунктуацию, опечатки и грамматические неверные слова:

{message}
"""
        messages = [{"content": message, "role": "user"}]

        translation = ""
        while translation == "":
            translation = ChatCompletion.create(
                model=model, stream=False, messages=messages, chatId=index, provider=provider
            )
            translation = self.restore_code_blocks(translation)
            print(
                f"...received translation of {file_path}, chunk length: {len(message)}, process: {process}, chunk {index+1} out of {length}"
            )
        return translation.strip().strip("```markdown").strip("`").strip().strip("'''").strip()

    def read_md_files(self, folder_path, language="English", model="gpt-4", split=3200):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    txt_file_path = os.path.join(
                        root, os.path.splitext(file)[0] + ".md!"
                    )
                    content = None
                    if os.path.exists(txt_file_path):
                        with open(txt_file_path, "r") as f:
                            content = f.read()
                    else:
                        with open(file_path, "r") as f:
                            content = f.read()
                            with open(txt_file_path, "w") as w:
                                w.write(content)

                    translation = self.translate_long_text(
                        content,
                        file_path=file_path,
                        split_len=split,
                        language=language,
                        model=model,
                    )
                    with open(file_path, "w") as md_file:
                        md_file.write(translation)
                    print(f"Wrote translation into {file_path}")

            for dir in dirs:
                dir_path = os.path.join(root, dir)
                self.read_md_files(dir_path, language=language, model=model)