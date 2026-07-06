#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";

const TODOIST_API_URL = "https://api.todoist.com/rest/v2";
const API_TOKEN = process.env.TODOIST_API_TOKEN;

if (!API_TOKEN) {
  console.error("Error: TODOIST_API_TOKEN environment variable is required");
  process.exit(1);
}

const api = axios.create({
  baseURL: TODOIST_API_URL,
  headers: {
    Authorization: `Bearer ${API_TOKEN}`,
  },
});

interface TodoistTask {
  id: string;
  content: string;
  description: string;
  project_id: string;
  labels: string[];
  priority: number;
  due?: {
    date: string;
    string: string;
  };
  url: string;
}

interface TodoistProject {
  id: string;
  name: string;
  color: string;
  is_favorite: boolean;
}

const server = new Server(
  {
    name: "mcp-todoist",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_tasks",
        description: "Get all active tasks, optionally filtered by project or label",
        inputSchema: {
          type: "object",
          properties: {
            project_id: {
              type: "string",
              description: "Filter tasks by project ID",
            },
            label: {
              type: "string",
              description: "Filter tasks by label name",
            },
          },
        },
      },
      {
        name: "create_task",
        description: "Create a new task in Todoist",
        inputSchema: {
          type: "object",
          properties: {
            content: {
              type: "string",
              description: "Task title/content",
            },
            description: {
              type: "string",
              description: "Task description (optional)",
            },
            project_id: {
              type: "string",
              description: "Project ID to add task to (optional)",
            },
            labels: {
              type: "array",
              items: { type: "string" },
              description: "Array of label names (optional)",
            },
            priority: {
              type: "number",
              description: "Priority from 1 (normal) to 4 (urgent)",
            },
            due_string: {
              type: "string",
              description: "Due date in natural language (e.g., 'tomorrow', 'next Monday')",
            },
          },
          required: ["content"],
        },
      },
      {
        name: "update_task",
        description: "Update an existing task",
        inputSchema: {
          type: "object",
          properties: {
            task_id: {
              type: "string",
              description: "ID of the task to update",
            },
            content: {
              type: "string",
              description: "New task content",
            },
            description: {
              type: "string",
              description: "New description",
            },
            labels: {
              type: "array",
              items: { type: "string" },
              description: "New labels array",
            },
            priority: {
              type: "number",
              description: "New priority (1-4)",
            },
            due_string: {
              type: "string",
              description: "New due date",
            },
          },
          required: ["task_id"],
        },
      },
      {
        name: "complete_task",
        description: "Mark a task as complete",
        inputSchema: {
          type: "object",
          properties: {
            task_id: {
              type: "string",
              description: "ID of the task to complete",
            },
          },
          required: ["task_id"],
        },
      },
      {
        name: "delete_task",
        description: "Delete a task permanently",
        inputSchema: {
          type: "object",
          properties: {
            task_id: {
              type: "string",
              description: "ID of the task to delete",
            },
          },
          required: ["task_id"],
        },
      },
      {
        name: "get_projects",
        description: "Get all projects",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "create_project",
        description: "Create a new project",
        inputSchema: {
          type: "object",
          properties: {
            name: {
              type: "string",
              description: "Project name",
            },
            color: {
              type: "string",
              description: "Project color (e.g., 'red', 'blue')",
            },
            is_favorite: {
              type: "boolean",
              description: "Whether to mark as favorite",
            },
          },
          required: ["name"],
        },
      },
      {
        name: "add_comment",
        description: "Add a comment to a task",
        inputSchema: {
          type: "object",
          properties: {
            task_id: {
              type: "string",
              description: "ID of the task to comment on",
            },
            content: {
              type: "string",
              description: "Comment content",
            },
          },
          required: ["task_id", "content"],
        },
      },
      {
        name: "get_comments",
        description: "Get all comments for a task",
        inputSchema: {
          type: "object",
          properties: {
            task_id: {
              type: "string",
              description: "ID of the task",
            },
          },
          required: ["task_id"],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "get_tasks": {
        let params: any = {};
        if (args?.project_id) params.project_id = args.project_id;
        if (args?.label) params.label = args.label;

        const response = await api.get("/tasks", { params });
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(response.data, null, 2),
            },
          ],
        };
      }

      case "create_task": {
        const taskData: any = {
          content: args?.content,
        };
        if (args?.description) taskData.description = args.description;
        if (args?.project_id) taskData.project_id = args.project_id;
        if (args?.labels) taskData.labels = args.labels;
        if (args?.priority) taskData.priority = args.priority;
        if (args?.due_string) taskData.due_string = args.due_string;

        const response = await api.post("/tasks", taskData);
        return {
          content: [
            {
              type: "text",
              text: `Task created successfully:\n${JSON.stringify(response.data, null, 2)}`,
            },
          ],
        };
      }

      case "update_task": {
        const updateData: any = {};
        if (args?.content) updateData.content = args.content;
        if (args?.description) updateData.description = args.description;
        if (args?.labels) updateData.labels = args.labels;
        if (args?.priority) updateData.priority = args.priority;
        if (args?.due_string) updateData.due_string = args.due_string;

        const response = await api.post(`/tasks/${args?.task_id}`, updateData);
        return {
          content: [
            {
              type: "text",
              text: `Task updated successfully:\n${JSON.stringify(response.data, null, 2)}`,
            },
          ],
        };
      }

      case "complete_task": {
        await api.post(`/tasks/${args?.task_id}/close`);
        return {
          content: [
            {
              type: "text",
              text: `Task ${args?.task_id} marked as complete`,
            },
          ],
        };
      }

      case "delete_task": {
        await api.delete(`/tasks/${args?.task_id}`);
        return {
          content: [
            {
              type: "text",
              text: `Task ${args?.task_id} deleted successfully`,
            },
          ],
        };
      }

      case "get_projects": {
        const response = await api.get("/projects");
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(response.data, null, 2),
            },
          ],
        };
      }

      case "create_project": {
        const projectData: any = {
          name: args?.name,
        };
        if (args?.color) projectData.color = args.color;
        if (args?.is_favorite !== undefined) projectData.is_favorite = args.is_favorite;

        const response = await api.post("/projects", projectData);
        return {
          content: [
            {
              type: "text",
              text: `Project created successfully:\n${JSON.stringify(response.data, null, 2)}`,
            },
          ],
        };
      }

      case "add_comment": {
        const response = await api.post("/comments", {
          task_id: args?.task_id,
          content: args?.content,
        });
        return {
          content: [
            {
              type: "text",
              text: `Comment added successfully:\n${JSON.stringify(response.data, null, 2)}`,
            },
          ],
        };
      }

      case "get_comments": {
        const response = await api.get("/comments", {
          params: { task_id: args?.task_id },
        });
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(response.data, null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error: ${error.response?.data?.message || error.message}`,
        },
      ],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Todoist MCP server running on stdio");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
