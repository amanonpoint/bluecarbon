# from llama_parse import LlamaParse


# parser = LlamaParse(
#    api_key="llx-IgsYSScWFtzDW5ZLOQ2GTOoOkhmhW0pOBSRvU7apk0M9yPil",  # if you did not create an environmental variable you can set the API key here
#    result_type="markdown",  # "markdown" and "text" are available,

#     extract_charts=True,

#     auto_mode=True,

#     auto_mode_trigger_on_image_in_page=True,

#     auto_mode_trigger_on_table_in_page=True,
#    )

# file_name = "utils\data\input\ISLR_1stEd-1-30.pdf"
# extra_info = {"file_name": file_name}

# with open(f"./{file_name}", "rb") as f:
#    # must provide extra_info with file_name key with passing file object
#    documents = parser.load_data(f, extra_info=extra_info)

# # with open('output.md', 'w') as f:
#    # print(documents, file=f)

# # Write the output to a file
# with open("utils\data\llamaOutput\llamaoutput.md", "w", encoding="utf-8") as f:
#    for doc in documents:
#        f.write(doc.text)