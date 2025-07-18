import { RefObject } from "react";

export const forceScrollToBottom = (
	chatContainerRef: RefObject<HTMLDivElement | null>
) => {
	if (chatContainerRef.current) {
		const container = chatContainerRef.current;
		container.scrollTop = container.scrollHeight + 3000;
	}
};

export const smoothScrollToBottom = (
	chatContainerRef: RefObject<HTMLDivElement | null>
) => {
	if (chatContainerRef.current) {
		const container = chatContainerRef.current;
		container.scrollTo({
			top: container.scrollHeight + 1000,
			behavior: "smooth",
		});
	}
};
