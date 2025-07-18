import React, { useRef, forwardRef } from "react";
import { chatAsciiBackground, goodbyeAscii } from "@/assets/ascii_art";
import { ChatMessageComponent } from "./ChatMessage";
import { TypingIndicator } from "./TypingIndicator";
import { ChatMessage } from "@/types";
import { userSaidBye } from "@/utils/chatUtils";

interface ChatContainerProps {
	messages: ChatMessage[];
	isTyping: boolean;
}

export const ChatContainer = forwardRef<HTMLDivElement, ChatContainerProps>(
	({ messages, isTyping }, ref) => {
		const messagesEndRef = useRef<HTMLDivElement>(null);

		return (
			<>
				{/* ASCII Background */}
				<div className="relative w-full flex flex-col items-center text-center">
					<pre className="text-white/50 text-[10px] leading-none select-none whitespace-pre-wrap px-2">
						{chatAsciiBackground}
					</pre>
				</div>

				{/* Catchphrase */}
				<div className="text-center mb-4">
					<h2 className="text-xl font-semibold text-white adamina-regular">
						what's on the playlist today?
					</h2>
				</div>

				{/* Chat content (scrollable area) */}
				<div
					ref={ref}
					className="flex-1 overflow-y-auto px-4 pb-40 container mx-auto max-w-4xl space-y-4"
				>
					{messages.length === 0 ? (
						<div className="text-center text-white/50 adamina-regular mt-8">
							Start a conversation by asking about music, playlists, or
							recommendations!
						</div>
					) : (
						messages.map((message) => (
							<ChatMessageComponent key={message.id} message={message} />
						))
					)}

					{isTyping && <TypingIndicator />}

					{/* Scroll target element - taller for better visibility */}
					<div ref={messagesEndRef} className="h-8" />

					{userSaidBye(messages) && (
						<div className="flex justify-center mt-6">
							<pre className="text-white/50 text-[12px] leading-none whitespace-pre-wrap text-center">
								{goodbyeAscii}
							</pre>
						</div>
					)}
				</div>
			</>
		);
	}
);

ChatContainer.displayName = "ChatContainer";
