import React from "react";
import ReactMarkdown from "react-markdown";
import {
	Carousel,
	CarouselContent,
	CarouselItem,
	CarouselNext,
	CarouselPrevious,
} from "@/components/ui/carousel";
import { ChatMessage } from "@/types";

interface ChatMessageComponentProps {
	message: ChatMessage;
}

export const ChatMessageComponent: React.FC<ChatMessageComponentProps> = ({
	message,
}) => {
	return (
		<div
			className={`flex flex-col ${message.role === "user" ? "items-end" : "items-start"} space-y-2`}
		>
			{/* Text Message */}
			<div
				className={`max-w-[70%] p-4 rounded-lg adamina-regular text-sm ${
					message.role === "user"
						? "bg-white text-black ml-4"
						: "bg-white/10 text-white  mr-4"
				}`}
			>
				<div className="whitespace-pre-wrap">
					<ReactMarkdown>{message.content}</ReactMarkdown>
				</div>
				<div className="text-xs opacity-60 mt-2">
					{message.timestamp.toLocaleTimeString()}
				</div>
			</div>

			{/* Spotify Images Carousel - Outside text bubble */}
			{message.spotifyImages && message.spotifyImages.length > 0 && (
				<div
					className={`w-full mt-2 ${
						message.role === "user" ? "mr-4 self-end" : "ml-4 self-start"
					}`}
				>
					<div className="max-w-max relative">
						<Carousel className="w-11/12">
							<CarouselContent className="-ml-1">
								{message.spotifyImages.map((image, index) => (
									<CarouselItem
										key={index}
										className="pl-1 md:basis-1/2 lg:basis-1/3"
									>
										<div className="p-1">
											<div className="aspect-square rounded-md overflow-hidden ">
												<img
													src={image.url}
													alt={image.title || "Spotify"}
													className="w-full h-full object-cover"
													onError={(e) => {
														const target = e.target as HTMLImageElement;
														target.style.display = "none";
													}}
												/>
											</div>
										</div>
									</CarouselItem>
								))}
							</CarouselContent>

							{message.spotifyImages.length > 1 && (
								<>
									<CarouselPrevious className="h-6 w-6 -left-3 text-black border-white hover:bg-white hover:text-black" />
									<CarouselNext className="h-6 w-6 -right-3 text-black  hover:bg-white hover:text-black" />
								</>
							)}
						</Carousel>
					</div>
				</div>
			)}
		</div>
	);
};
