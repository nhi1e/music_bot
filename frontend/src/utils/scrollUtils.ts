import { RefObject } from "react";

export const forceScrollToBottom = (
	chatContainerRef: RefObject<HTMLDivElement | null>,
	messagesEndRef: RefObject<HTMLDivElement | null>
) => {
	if (chatContainerRef.current) {
		const container = chatContainerRef.current;
		container.scrollTop = container.scrollHeight + 3000;
	}
	if (messagesEndRef.current) {
		messagesEndRef.current.scrollIntoView({
			block: "end",
			inline: "nearest",
		});
	}
};

export const smoothScrollToBottom = (
	chatContainerRef: RefObject<HTMLDivElement | null>,
	messagesEndRef: RefObject<HTMLDivElement | null>
) => {
	if (chatContainerRef.current) {
		const container = chatContainerRef.current;
		container.scrollTop = container.scrollHeight + 1000;
	}

	if (messagesEndRef.current) {
		messagesEndRef.current.scrollIntoView({
			behavior: "smooth",
			block: "end",
			inline: "nearest",
		});
	}
};
