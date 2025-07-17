import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
	Carousel,
	CarouselContent,
	CarouselItem,
	CarouselNext,
	CarouselPrevious,
} from "@/components/ui/carousel";
import ReactMarkdown from "react-markdown";
import {
	asciiBackground,
	chatAsciiBackground,
	goodbyeAscii,
} from "@/assets/ascii_art";

interface SpotifyUser {
	id: string;
	display_name: string;
	email?: string;
	followers: number;
	images?: Array<{ url: string; height: number; width: number }>;
}

interface ChatMessage {
	id: string;
	content: string;
	role: "user" | "assistant";
	timestamp: Date;
	spotifyImages?: Array<{
		url: string;
		title?: string;
		subtitle?: string;
		type?: "album" | "artist" | "playlist" | "track";
	}>;
}

function App() {
	const [isAuthenticated, setIsAuthenticated] = useState(false);
	const [isLoading, setIsLoading] = useState(true);
	const [user, setUser] = useState<SpotifyUser | null>(null);
	const [messages, setMessages] = useState<ChatMessage[]>([]);
	const [inputValue, setInputValue] = useState("");
	const [isTyping, setIsTyping] = useState(false);
	const chatContainerRef = useRef<HTMLDivElement>(null);
	const messagesEndRef = useRef<HTMLDivElement>(null);

	// Utility function for aggressive scrolling
	const forceScrollToBottom = () => {
		if (chatContainerRef.current) {
			const container = chatContainerRef.current;
			// Force immediate scroll without smooth behavior
			container.scrollTop = container.scrollHeight + 3000;
		}
		if (messagesEndRef.current) {
			messagesEndRef.current.scrollIntoView({
				block: "end",
				inline: "nearest",
			});
		}
	};

	// Extract Spotify images from response and return both images and cleaned text
	const extractSpotifyImages = (responseText: string) => {
		console.log("🔍 Extracting Spotify images from response:", responseText);
		console.log("🔍 Response text length:", responseText.length);

		const images: Array<{
			url: string;
			title?: string;
			subtitle?: string;
			type?: "album" | "artist" | "playlist" | "track";
		}> = [];

		let cleanedText = responseText;

		try {
			// Look for markdown image patterns to extract URLs and remove from text
			const markdownImagePatterns = [
				/!\[.*?\]\((https:\/\/[^)]+)\)/g,
				/!\[Artist:.*?\]\((https:\/\/[^)]+)\)/g,
				/!\[Track:.*?\]\((https:\/\/[^)]+)\)/g,
				/!\[Album:.*?\]\((https:\/\/[^)]+)\)/g,
			];

			const foundUrls: string[] = [];
			const markdownMatches: string[] = [];

			markdownImagePatterns.forEach((pattern, index) => {
				console.log(
					`📸 Testing markdown pattern ${index + 1}:`,
					pattern.source
				);
				const matches = responseText.match(pattern);
				console.log(`📸 Pattern ${index + 1} matches:`, matches);
				if (matches) {
					markdownMatches.push(...matches);
					const urlMatches = matches
						.map((match) => {
							console.log("📸 Processing match:", match);
							const urlMatch = match.match(/\(([^)]+)\)/);
							console.log("📸 Extracted URL:", urlMatch ? urlMatch[1] : null);
							return urlMatch ? urlMatch[1] : null;
						})
						.filter((url): url is string => url !== null);
					foundUrls.push(...urlMatches);
				}
			});

			// Remove all markdown image syntax from the text
			markdownMatches.forEach((match) => {
				cleanedText = cleanedText.replace(match, "").replace(/\n\n\n/g, "\n\n");
			});

			// Also look for direct Spotify URLs (fallback)
			const directUrlPatterns = [
				/https:\/\/i\.scdn\.co\/image\/[a-f0-9]{32}/g,
				/https:\/\/mosaic\.scdn\.co\/640\/[a-f0-9]{32}/g,
				/https:\/\/lineup-images\.scdn\.co\/[^"'\s]+/g,
				/https:\/\/.*\.spotifycdn\.com\/[^"'\s]+/g,
			];

			directUrlPatterns.forEach((pattern) => {
				const matches = responseText.match(pattern);
				if (matches) {
					foundUrls.push(...matches);
				}
			});

			console.log("🎵 Found image URLs:", foundUrls);

			if (foundUrls.length > 0) {
				// Remove duplicates and limit to 5 images
				const uniqueUrls = foundUrls.filter(
					(url, index) => foundUrls.indexOf(url) === index
				);
				const limitedUrls = uniqueUrls.slice(0, 5);

				console.log("✨ Processing unique URLs:", limitedUrls);

				limitedUrls.forEach((url, index) => {
					console.log(`🖼️ Processing URL ${index + 1}:`, url);

					// Try to determine the type based on URL patterns
					let type: "album" | "artist" | "playlist" | "track" = "album";

					if (url.includes("mosaic")) {
						type = "playlist";
						console.log("🎵 Detected playlist type");
					} else if (url.includes("lineup-images")) {
						type = "artist";
						console.log("🎤 Detected artist type");
					} else if (url.includes("i.scdn.co")) {
						// Check the original response to see if this was an artist or track image
						const urlIndex = responseText.indexOf(url);
						if (urlIndex !== -1) {
							const contextBefore = responseText.substring(
								Math.max(0, urlIndex - 100),
								urlIndex
							);
							if (contextBefore.includes("Artist:")) {
								type = "artist";
								console.log("🎤 Detected artist type from context");
							} else if (contextBefore.includes("Track:")) {
								type = "track";
								console.log("🎵 Detected track type from context");
							}
						}
					}

					images.push({
						url,
						type,
					});

					console.log(
						`✅ Added image: type=${type}, url=${url.substring(0, 50)}...`
					);
				});
			} else {
				console.log("❌ No image URLs found in response");
			}

			console.log("🖼️ Final extracted images:", images);
			console.log("📝 Cleaned text:", cleanedText);
		} catch (error) {
			console.error("❌ Error extracting Spotify images:", error);
		}

		return { images, cleanedText };
	};

	useEffect(() => {
		const checkAuth = async () => {
			// Check for auth callback parameters in URL
			const urlParams = new URLSearchParams(window.location.search);
			const authStatus = urlParams.get("auth");
			const username = urlParams.get("user");
			const errorMessage = urlParams.get("message");

			if (authStatus === "success") {
				// Clear URL parameters
				window.history.replaceState({}, document.title, "/");
				setIsAuthenticated(true);
				setIsLoading(false);
				return;
			}

			if (authStatus === "error") {
				// Clear URL parameters
				window.history.replaceState({}, document.title, "/");
				alert(
					`Authentication failed: ${decodeURIComponent(errorMessage || "Unknown error")}`
				);
				setIsLoading(false);
				return;
			}

			if (authStatus === "denied") {
				// Clear URL parameters
				window.history.replaceState({}, document.title, "/");
				alert("You denied access to Spotify. Please try again.");
				setIsLoading(false);
				return;
			}

			// Check if user is already authenticated via API
			try {
				const response = await fetch("http://localhost:8080/auth/status");
				const data = await response.json();
				setIsAuthenticated(data.authenticated);
				if (data.authenticated && data.user) {
					setUser(data.user);
				}
			} catch (error) {
				console.error("Error checking auth status:", error);
				setIsAuthenticated(false);
			}

			setIsLoading(false);
		};

		checkAuth();
	}, []);

	// Auto-scroll to the latest message - aggressive approach
	useEffect(() => {
		const scrollToBottom = () => {
			// Method 1: Scroll container to max height
			if (chatContainerRef.current) {
				const container = chatContainerRef.current;
				container.scrollTop = container.scrollHeight + 1000; // Extra padding to ensure full scroll
			}

			// Method 2: Scroll to end element with multiple attempts
			if (messagesEndRef.current) {
				messagesEndRef.current.scrollIntoView({
					behavior: "smooth",
					block: "end",
					inline: "nearest",
				});
			}
		};

		// Multiple scroll attempts with increasing delays
		const timeouts = [
			setTimeout(scrollToBottom, 50),
			setTimeout(scrollToBottom, 150),
			setTimeout(scrollToBottom, 300),
			setTimeout(forceScrollToBottom, 500), // Use utility function for final scroll
			setTimeout(forceScrollToBottom, 800), // Extra attempt
		];

		return () => timeouts.forEach(clearTimeout);
	}, [messages, isTyping]);

	const handleSpotifyLogin = () => {
		const backendUrl = "http://localhost:8080";
		window.location.href = `${backendUrl}/auth/spotify`;
	};

	const handleLogout = async () => {
		try {
			await fetch("http://localhost:8080/auth/logout", { method: "POST" });
			setIsAuthenticated(false);
			setUser(null);
			setMessages([]);
		} catch (error) {
			console.error("Error logging out:", error);
		}
	};

	const handleSendMessage = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!inputValue.trim()) return;

		const userMessage: ChatMessage = {
			id: Date.now().toString(),
			content: inputValue,
			role: "user",
			timestamp: new Date(),
		};

		setMessages((prev) => [...prev, userMessage]);
		setInputValue("");
		setIsTyping(true);

		// Aggressive scroll to bottom after adding user message
		setTimeout(() => {
			if (chatContainerRef.current) {
				chatContainerRef.current.scrollTop =
					chatContainerRef.current.scrollHeight + 1000;
			}
			if (messagesEndRef.current) {
				messagesEndRef.current.scrollIntoView({
					behavior: "smooth",
					block: "end",
				});
			}
		}, 50);

		setTimeout(() => {
			if (chatContainerRef.current) {
				chatContainerRef.current.scrollTop =
					chatContainerRef.current.scrollHeight + 1000;
			}
		}, 200);

		try {
			const response = await fetch("http://localhost:8080/chat", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ message: inputValue }),
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			const responseContent =
				data.response || "Sorry, I couldn't process your request.";
			const { images: spotifyImages, cleanedText } =
				extractSpotifyImages(responseContent);

			console.log("🎵 Response from backend:", responseContent);
			console.log("🖼️ Extracted Spotify images:", spotifyImages);
			console.log("📝 Cleaned text:", cleanedText);

			const aiMessage: ChatMessage = {
				id: (Date.now() + 1).toString(),
				content: cleanedText, // Use cleaned text without image markdown
				role: "assistant",
				timestamp: new Date(),
				spotifyImages: spotifyImages.length > 0 ? spotifyImages : undefined,
			};

			console.log("💬 AI message with images:", aiMessage);

			setMessages((prev) => [...prev, aiMessage]);

			// Aggressive scroll to bottom after adding AI message
			setTimeout(() => {
				if (chatContainerRef.current) {
					chatContainerRef.current.scrollTop =
						chatContainerRef.current.scrollHeight + 1000;
				}
				if (messagesEndRef.current) {
					messagesEndRef.current.scrollIntoView({
						behavior: "smooth",
						block: "end",
					});
				}
			}, 50);

			setTimeout(() => {
				if (chatContainerRef.current) {
					chatContainerRef.current.scrollTop =
						chatContainerRef.current.scrollHeight + 1000;
				}
			}, 200);

			setTimeout(() => {
				if (chatContainerRef.current) {
					chatContainerRef.current.scrollTop =
						chatContainerRef.current.scrollHeight + 1000;
				}
			}, 500);
		} catch (error) {
			console.error("Error sending message:", error);
			const errorMessage: ChatMessage = {
				id: (Date.now() + 1).toString(),
				content:
					"Sorry, there was an error processing your request. Please try again.",
				role: "assistant",
				timestamp: new Date(),
			};
			setMessages((prev) => [...prev, errorMessage]);

			// Aggressive scroll to bottom after adding error message
			setTimeout(() => {
				if (chatContainerRef.current) {
					chatContainerRef.current.scrollTop =
						chatContainerRef.current.scrollHeight + 1000;
				}
				if (messagesEndRef.current) {
					messagesEndRef.current.scrollIntoView({
						behavior: "smooth",
						block: "end",
					});
				}
			}, 50);

			setTimeout(() => {
				if (chatContainerRef.current) {
					chatContainerRef.current.scrollTop =
						chatContainerRef.current.scrollHeight + 1000;
				}
			}, 200);
		} finally {
			setIsTyping(false);
		}
	};

	const userSaidBye = (messages: ChatMessage[]) => {
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

	if (isLoading) {
		return (
			<div className="min-h-screen bg-black flex items-center justify-center">
				<div className="h-8 w-8 border-2 border-white border-b-transparent rounded-full animate-spin"></div>
			</div>
		);
	}

	if (!isAuthenticated) {
		return (
			<div className="relative min-h-screen bg-black flex items-center justify-center px-4 overflow-hidden">
				<pre className="absolute inset-0 text-white text-[20px] leading-none pointer-events-none z-0 select-none p-2 whitespace-pre-wrap">
					{asciiBackground}
				</pre>
				<div className="w-full max-w-sm text-white text-center space-y-6">
					<h1 className="text-7xl pinyon-script-regular">Personal Music Bot</h1>
					<button
						onClick={handleSpotifyLogin}
						className="w-full bg-black border border-white text-white adamina-regular font-semibold py-4 px-6 transition-all duration-200 transform flex items-center justify-center space-x-3 hover:shadow-[4px_4px_0_white] hover:translate-x-[-1px] hover:translate-y-[-1px]"
					>
						Continue with Spotify
					</button>
				</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen bg-black text-white flex flex-col font-mono">
			{/* Header */}
			<div className="sticky top-0 z-50 bg-black">
				<div className="container mx-auto px-4 py-5 flex justify-between items-center">
					<h1 className="text-2xl pinyon-script-regular">Personal Music Bot</h1>
					<div className="flex items-center space-x-4">
						{user && (
							<div className="flex items-center space-x-3">
								<span className="text-sm adamina-regular">
									{user.display_name || user.id}
								</span>
								<DropdownMenu>
									<DropdownMenuTrigger>
										<Avatar className="h-8 w-8 border border-white/20">
											<AvatarImage
												src={
													user.images && user.images.length > 0
														? user.images[0].url
														: undefined
												}
												alt={user.display_name || user.id}
											/>
											<AvatarFallback className="bg-white/10 text-white text-xs adamina-regular">
												{(user.display_name || user.id).charAt(0).toUpperCase()}
											</AvatarFallback>
										</Avatar>
									</DropdownMenuTrigger>
									<DropdownMenuContent className="w-auto min-w-[6rem]">
										<DropdownMenuItem
											onClick={handleLogout}
											className="cursor-pointer adamina-regular text-black hover:bg-white/10 focus:bg-white/10 px-2 py-2"
										>
											Logout
										</DropdownMenuItem>
									</DropdownMenuContent>
								</DropdownMenu>
							</div>
						)}
					</div>
				</div>
			</div>

			{/* ASCII Background */}
			<div className="relative w-full flex flex-col items-center text-center">
				<pre className="text-white/50 text-[10px] leading-none select-none whitespace-pre-wrap px-2">
					{chatAsciiBackground}
				</pre>
			</div>

			{/* Catchphrase */}
			<div className="text-center mb-4">
				<h2 className="text-xl font-semibold text-white adamina-regular">
					what’s on the playlist today?
				</h2>
			</div>

			{/* Chat content (scrollable area) */}
			<div
				ref={chatContainerRef}
				className="flex-1 overflow-y-auto px-4 pb-40 container mx-auto max-w-4xl space-y-4"
			>
				{messages.length === 0 ? (
					<div className="text-center text-white/50 adamina-regular mt-8">
						Start a conversation by asking about music, playlists, or
						recommendations!
					</div>
				) : (
					messages.map((message) => (
						<div
							key={message.id}
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
										message.role === "user"
											? "mr-4 self-end"
											: "ml-4 self-start"
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
					))
				)}

				{isTyping && (
					<div className="flex justify-start">
						<div className="max-w-[70%] p-4 rounded-lg bg-white/10 text-white mr-4 adamina-regular">
							<div className="flex items-center space-x-2">
								<div className="flex space-x-1">
									<div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
									<div className="w-2 h-2 bg-white rounded-full animate-pulse animation-delay-75"></div>
									<div className="w-2 h-2 bg-white rounded-full animate-pulse animation-delay-150"></div>
								</div>
								<span className="text-white/60 text-sm">Typing...</span>
							</div>
						</div>
					</div>
				)}

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

			{/* Sticky input box at the bottom */}
			<div className="sticky adamina-regular bottom-0 left-0 w-full bg-black z-50">
				<form
					onSubmit={handleSendMessage}
					className="container mx-auto px-4 py-4 max-w-4xl flex space-x-2"
				>
					<Input
						type="text"
						placeholder="Ask about music, playlists, or get recommendations..."
						value={inputValue}
						onChange={(e) => setInputValue(e.target.value)}
						className="flex-1 bg-black border-white text-white placeholder:text-white/50 focus:border-white focus:ring-white/50"
						disabled={isTyping}
					/>
					<Button
						type="submit"
						variant="outline"
						className="border-white text-black hover:shadow-[2px_2px_0_white] hover:translate-x-[-1px] hover:translate-y-[-1px] disabled:opacity-50"
						disabled={isTyping || !inputValue.trim()}
					>
						Send
					</Button>
				</form>
			</div>
		</div>
	);
}
export default App;
