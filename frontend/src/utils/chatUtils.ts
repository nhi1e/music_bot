import { ChatMessage } from "@/types";

export const userSaidBye = (messages: ChatMessage[]): boolean => {
	if (messages.length < 2) return false;
	const lastUserMessage = [...messages]
		.reverse()
		.find((m) => m.role === "user");
	if (!lastUserMessage) return false;

	const content = lastUserMessage.content.toLowerCase();
	return (
		content.includes("bye") ||
		content.includes("exit") ||
		content.includes("quit")
	);
};
