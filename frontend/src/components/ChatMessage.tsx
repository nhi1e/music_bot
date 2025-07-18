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
import SpotifyWrappedCard from "./SpotifyWrapped";

interface ChatMessageComponentProps {
	message: ChatMessage;
}

export const ChatMessageComponent: React.FC<ChatMessageComponentProps> = ({
	message,
}) => {
	// Calculate dynamic carousel sizing
	const getCarouselClasses = (imageCount: number) => {
		const count = Math.min(imageCount, 5);
		const basisClass = (() => {
			switch (count) {
				case 1:
					return "basis-full";
				case 2:
					return "md:basis-1/2";
				case 3:
					return "md:basis-1/2 lg:basis-1/3";
				case 4:
					return "md:basis-1/2 lg:basis-1/4";
				default:
					return "md:basis-1/2 lg:basis-1/5";
			}
		})();
		const carouselWidth = (() => {
			switch (count) {
				case 1:
					return "w-48";
				case 2:
					return "w-96";
				case 3:
					return "w-[36rem]";
				case 4:
					return "w-[48rem]";
				default:
					return "w-[60rem]";
			}
		})();
		return { basisClass, carouselWidth };
	};

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

			{/* Spotify Wrapped Card */}
			{message.spotifyWrapped && (
				<div
					className={`w-full mt-4 flex ${
						message.role === "user" ? "justify-end mr-4" : "justify-start ml-4"
					}`}
				>
					<SpotifyWrappedCard data={message.spotifyWrapped} />
				</div>
			)}

			{/* Spotify Images Carousel - Outside text bubble */}
			{message.spotifyImages && message.spotifyImages.length > 0 && (
				<div
					className={`w-full mt-2 ${
						message.role === "user" ? "mr-4 self-end" : "self-start"
					}`}
				>
					<div className="max-w-max relative">
						{(() => {
							const { basisClass, carouselWidth } = getCarouselClasses(
								message.spotifyImages.length
							);
							const imagesToShow = message.spotifyImages.slice(0, 5);

							return (
								<Carousel className={`${carouselWidth} max-w-full`}>
									<CarouselContent className="-ml-1">
										{imagesToShow.map((image, index) => (
											<CarouselItem
												key={index}
												className={`pl-1 ${basisClass}`}
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
								</Carousel>
							);
						})()}
					</div>
				</div>
			)}
		</div>
	);
};
