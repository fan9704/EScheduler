import DiscordIcon from "@/assets/icons/discord.webp";
import SlackIcon from "@/assets/icons/slack.webp";
import TeamsIcon from "@/assets/icons/teams.webp";
import TelegramIcon from "@/assets/icons/telegram.webp";
import type { WebhookTemplate } from "@/models/schedule_helper";

const webhook_template: WebhookTemplate[] = [
	{
		id: 1,
		name: "Discord",
		image: DiscordIcon,
		body: {
			content: "Hello from EScheduler!",
			username: "EScheduler Bot",
			avatar_url:
				"https://private-user-images.githubusercontent.com/76801598/481695339-a4761d01-3fba-46c1-b58a-8575651da82c.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTc2NDY1MTEsIm5iZiI6MTc1NzY0NjIxMSwicGF0aCI6Ii83NjgwMTU5OC80ODE2OTUzMzktYTQ3NjFkMDEtM2ZiYS00NmMxLWI1OGEtODU3NTY1MWRhODJjLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTA5MTIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwOTEyVDAzMDMzMVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWQxN2VmOWM1ZjQyYjQzNDc4MDU2MTFlYTA5YmVmMzYwMmZkYTZkYmI4YmM2NzRiZTZhNDg3MmM5YTJmZjYyNjYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.744R28_DppAth7R01DVR7KO7WxF4LfQGtZ3WCottNfk",
			embeds: [
				{
					title: "Task Notification",
					description: "This is a notification from your scheduled task.",
					color: 5814783,
				},
			],
			allow_mentions: {
				parse: ["users", "roles", "everyone"],
			},
		},
	},
	{
		id: 2,
		name: "Slack",
		image: SlackIcon,
		body: {
			text: "Hello from EScheduler!",
			username: "EScheduler Bot",
			icon_emoji: ":robot_face:",
		},
	},
	{
		id: 3,
		name: "Microsoft Teams",
		image: TeamsIcon,
		body: {
			"@type": "MessageCard",
			"@context": "http://schema.org/extensions",
			summary: "Task Notification",
			themeColor: "0076D7",
			title: "Task Notification",
			text: "This is a notification from your scheduled task.",
		},
	},
	{
		id: 4,
		name: "Telegram",
		image: TelegramIcon,
		body: {
			chat_id: "YOUR_CHAT_ID",
			text: "Hello from EScheduler!",
			parse_mode: "Markdown",
		},
	},
];

export { webhook_template };
