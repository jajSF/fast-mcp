from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI, HTTPException
import aiohttp
import asyncio

mcp = FastMCP()
app = FastAPI()
space_id = 90183836477
CLICKUP_AUTHENTICATION_TOKEN="pk_89666898_PD9CCKVDEGQ1P6DLIBJ3PN9BJ9KQH00C"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": CLICKUP_AUTHENTICATION_TOKEN
}

# Helper function
async def fetch_url(session: aiohttp.ClientSession, url: str):
    """
    Used to fetch URLs asynchronously.
    :param session: The aiohttp session to use for the request.
    :param url: The URL to fetch.
    :return: The JSON response from the URL.
    """
    async with session.get(url, headers=headers) as response:
        if response.status != 200:
            raise HTTPException(status_code=response.status, detail=await response.text())
        try:
            return await response.json()
        except ValueError:
            raise HTTPException(status_code=500, detail="Invalid JSON response")
        
# FastMCP instance
@mcp.tool()
async def get_task_details(user_id: int):
    """
    Description: Fetches tasks assigned to a user from ClickUp API.
    Args: userId (int): The ID of the user whose tasks are to be fetched.
    Returns: A dictionary containing tasks categorized by their status (to do, in progress, complete).
    """
    # initializing the task map
    task_map = {
        "to do": [],
        "in progress": [],
        "complete": []
    }

    async with aiohttp.ClientSession() as session:
        # fetch folders
        folders_url = f"https://api.clickup.com/api/v2/space/{space_id}/folder"
        folders_data = await fetch_url(session, folders_url)
        folders = folders_data.get("folders", [])

        # collect all the list URLs
        list_urls = []
        for folder in folders:
            lists_url = f"https://api.clickup.com/api/v2/folder/{folder['id']}/list"
            lists_data = await fetch_url(session, lists_url)
            lists = lists_data.get("lists", [])
            
            for lst in lists:
                task_urls = (
                    f"https://api.clickup.com/api/v2/list/{lst['id']}/task?include_closed=true&assignees[]={user_id}&"
                )
                list_urls.append((task_urls, lst["name"]))

        tasks_responses = await asyncio.gather(
            *(fetch_url(session, url) for url, _ in list_urls),
            return_exceptions=True
        )

        # Process tasks
        for (tasks_url, list_name), task_data in zip(list_urls, tasks_responses):
            if isinstance(task_data, Exception):
                continue  # Skip this URL if there was an error
            tasks = task_data.get("tasks", [])
            for task in tasks:
                status = task["status"]["status"]
                task_info = {
                    "id":task['id'],
                    "task_name": task['name'],
                    "list_name": list_name,
                }
                if status == "complete":
                    task_info["date_closed"] = task.get("date_closed")
                task_map[status].append(task_info)
    
    return task_map


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')