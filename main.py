import asyncio
import logging
import os
import re
import random
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page, FrameLocator, BrowserContext
from playwright._impl._errors import Error as PlaywrightError, TargetClosedError
from colorama import Fore, Back, Style, init
from typing import Dict, Optional

# Initialize colorama for colored output
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter for colored logging output"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_color = self.COLORS.get(record.levelname, Fore.WHITE)
        record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        record.msg = f"{log_color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)


# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Apply colored formatter
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.handlers = [handler]

# Load environment variables
load_dotenv()


def log_success(message: str) -> None:
    """Log successful operations"""
    print(f"{Fore.GREEN + Style.BRIGHT}✓ {message}{Style.RESET_ALL}")


def log_error(message: str) -> None:
    """Log errors"""
    print(f"{Fore.RED + Style.BRIGHT}✗ {message}{Style.RESET_ALL}")


def log_warning(message: str) -> None:
    """Log warnings"""
    print(f"{Fore.YELLOW + Style.BRIGHT}⚠ {message}{Style.RESET_ALL}")


def log_info(message: str) -> None:
    """Log information"""
    print(f"{Fore.CYAN + Style.BRIGHT}ℹ {message}{Style.RESET_ALL}")


def log_step(message: str) -> None:
    """Log process steps"""
    print(f"{Fore.BLUE + Style.BRIGHT}➤ {message}{Style.RESET_ALL}")


def log_quest(message: str) -> None:
    """Log quests"""
    print(f"{Fore.MAGENTA + Style.BRIGHT}🎯 {message}{Style.RESET_ALL}")


def log_purchase(message: str) -> None:
    """Log purchases"""
    print(f"{Fore.GREEN + Back.BLACK + Style.BRIGHT}💰 {message}{Style.RESET_ALL}")


async def navigate_to_monad_spin(page: Page, shutdown_event: asyncio.Event) -> Optional[FrameLocator]:
    """
    Navigate to Monad Spin app and return the iframe locator
    
    Args:
        page: Playwright page object
        shutdown_event: Event to check for shutdown signal
        
    Returns:
        FrameLocator: Locator for the Monad Spin iframe, or None if shutdown requested
    """
    try:
        log_step("Navigating to farcaster.xyz...")
        await page.goto("https://farcaster.xyz")
        
        if shutdown_event.is_set():
            log_warning("Shutdown requested during page load")
            return None
            
        await page.wait_for_load_state('networkidle')
        log_success("Page loaded successfully")
        
        log_step("Looking for Mini Apps section...")
        if shutdown_event.is_set():
            return None
            
        await page.click('a[href="/miniapps"]', timeout=10000)
        log_success("Mini Apps section found and clicked")

        log_step("Looking for View All button...")
        if shutdown_event.is_set():
            return None
            
        await page.click('button:has-text("View All")', timeout=10000)
        log_success("View All button clicked")
        
        log_step("Looking for Monad Spin app...")
        if shutdown_event.is_set():
            return None
            
        await page.wait_for_selector('img[alt="Monad Spin"]', timeout=10000)
        log_success("Monad Spin app found")
        
        log_step("Clicking on Monad Spin...")
        await page.locator('text=Monad Spin').first.click()
        await page.wait_for_timeout(10000)
        log_success("Monad Spin launched")
        
        log_step("Waiting for iframe to load...")
        if shutdown_event.is_set():
            return None
            
        await page.wait_for_selector('iframe[src="https://monadspin.xyz"]', timeout=20000)
        frame = page.frame_locator('iframe[src="https://monadspin.xyz"]')
        log_success("Iframe loaded")
        
        return frame
        
    except (PlaywrightError, TargetClosedError) as e:
        if shutdown_event.is_set():
            log_info("Navigation cancelled due to shutdown request")
            return None
        log_error(f"Navigation error: {str(e)}")
        raise
    except Exception as e:
        log_error(f"Unexpected navigation error: {str(e)}")
        raise


async def switch_to_monad_testnet(frame: FrameLocator, shutdown_event: asyncio.Event) -> None:
    """
    Switch to Monad Testnet if the button is available
    
    Args:
        frame: FrameLocator for the Monad Spin iframe
        shutdown_event: Event to check for shutdown signal
    """
    if shutdown_event.is_set():
        return
        
    log_step("Looking for Switch to Monad Testnet button...")
    try:
        switch_button = frame.locator('button:has-text("Switch to Monad Testnet")')
        await switch_button.wait_for(state='visible', timeout=15000)
        log_success("Switch to Monad Testnet button found")
        
        if shutdown_event.is_set():
            return
            
        await switch_button.click()
        log_success("Successfully clicked Switch to Monad Testnet button")
        
        await asyncio.sleep(2)
    except Exception as e:
        if not shutdown_event.is_set():
            log_step(f"Switch to Monad Testnet button not found, continuing... ({str(e)})")


async def close_modal(page: Page, shutdown_event: asyncio.Event) -> None:
    """
    Close the modal window
    
    Args:
        page: Playwright page object
        shutdown_event: Event to check for shutdown signal
    """
    if shutdown_event.is_set():
        return
        
    log_step("Closing modal...")
    try:
        close_button = await page.wait_for_selector('button:has(svg.octicon-x)', timeout=10000)
        log_success("Close button found")
        
        if shutdown_event.is_set():
            return
            
        await close_button.click()
        log_success("Successfully clicked Close button")
        
        await page.wait_for_timeout(1000)
        log_success("Modal closed")
    except Exception as e:
        if not shutdown_event.is_set():
            log_error(f"Close button not found or could not be clicked: {str(e)}")
            raise


async def parse_remaining_spins(frame: FrameLocator) -> int:
    """
    Parse the number of remaining spins
    
    Args:
        frame: FrameLocator for the Monad Spin iframe
        
    Returns:
        int: Number of remaining spins (default: 3000 if parsing fails)
    """
    log_step("Parsing remaining spins count...")
    try:
        spins_remaining_element = frame.locator(
            'div:has-text("Spins Remaining")'
        ).locator('..').locator('div.text-2xl.font-bold.text-white').first
        
        spins_text = await spins_remaining_element.text_content()
        log_info(f"Raw spins text: {spins_text}")
        
        spins_match = re.search(r'\d+', spins_text)
        
        if spins_match:
            total_spins = int(spins_match.group())
            log_success(f"📊 Spins Remaining: {total_spins}")
            return total_spins
        else:
            log_warning("Could not parse spins, using default: 3000")
            return 3000
            
    except Exception as e:
        log_error(f"Error parsing spins count: {str(e)}, using default: 3000")
        return 3000


async def confirm_transaction(page: Page, shutdown_event: asyncio.Event) -> None:
    """
    Confirm the wallet transaction
    
    Args:
        page: Playwright page object
        shutdown_event: Event to check for shutdown signal
    """
    if shutdown_event.is_set():
        return
        
    try:
        wallet_iframe_selector = "iframe[src^='https://wallet.farcaster.xyz/MiniAppTransactionModal']"
        
        log_step("💳 Waiting for wallet modal...")
        await page.wait_for_selector(wallet_iframe_selector, state="attached", timeout=10000)
        
        iframe_element = await page.query_selector(wallet_iframe_selector)
        wallet_frame = await iframe_element.content_frame()
        
        if not wallet_frame:
            raise Exception("Wallet frame content not accessible")
        
        log_success("Wallet modal found")
        
        if shutdown_event.is_set():
            log_info("Skipping transaction confirmation due to shutdown")
            return
        
        try:
            await wallet_frame.wait_for_selector("div:has-text('Confirm transaction')", timeout=10000)
            await asyncio.sleep(10)
            log_step("Transaction confirmation dialog found")
        except Exception as e:
            log_step(f"Transaction confirmation dialog not found immediately: {str(e)}")
        
        if shutdown_event.is_set():
            return
            
        log_step("✅ Confirming transaction...")
        
        # Try different methods to find and click Confirm button
        confirm_clicked = False
        
        try:
            confirm_button = await wallet_frame.wait_for_selector('text="Confirm"', timeout=10000)
            await confirm_button.click()
            confirm_clicked = True
            log_success("Clicked Confirm button (method 1)")
        except:
            try:
                confirm_button = await wallet_frame.wait_for_selector('button:has-text("Confirm")', timeout=10000)
                await confirm_button.click()
                confirm_clicked = True
                log_success("Clicked Confirm button (method 2)")
            except:
                try:
                    confirm_button = await wallet_frame.wait_for_selector('[role="button"]:has-text("Confirm")', timeout=10000)
                    await asyncio.sleep(10)
                    await confirm_button.click()
                    await asyncio.sleep(10)
                    confirm_clicked = True
                    log_success("Clicked Confirm button (method 3)")
                except Exception as e:
                    log_error(f"Failed to click Confirm button: {str(e)}")
        
        if not confirm_clicked:
            log_warning("Could not click Confirm button with any method")
            return
        
        # Wait for modal to close
        try:
            await page.wait_for_selector(wallet_iframe_selector, state="hidden", timeout=15000)
            log_success("💳 Wallet modal closed")
        except:
            iframe_exists = await page.locator(wallet_iframe_selector).count()
            if iframe_exists == 0:
                log_success("💳 Wallet modal closed (verified)")
            else:
                log_warning("⚠️ Wallet modal may still be open")

        await page.wait_for_timeout(1000)
        
    except Exception as e:
        if not shutdown_event.is_set():
            log_step(f"Transaction confirmation not needed or failed: {str(e)}")


async def process_spin_result(
    frame: FrameLocator, 
    page: Page, 
    wins: int, 
    losses: int, 
    total_winnings: Dict[str, float],
    shutdown_event: asyncio.Event
) -> tuple[int, int]:
    """
    Process the result of a spin
    
    Args:
        frame: FrameLocator for the Monad Spin iframe
        page: Playwright page object
        wins: Current number of wins
        losses: Current number of losses
        total_winnings: Dictionary tracking total winnings by currency
        shutdown_event: Event to check for shutdown signal
        
    Returns:
        tuple: Updated (wins, losses) counts
    """
    await asyncio.sleep(3)
    
    congratulations = frame.locator('h2:has-text("CONGRATULATIONS")')
    no_win = frame.locator('h2:has-text("Better luck next time")')
    
    congratulations_count = await congratulations.count()
    no_win_count = await no_win.count()
    
    if congratulations_count > 0:
        wins += 1
        log_success(f"🎉 WIN! Total wins: {wins}")
        
        # Parse winnings amount
        try:
            win_amount_element = frame.locator('.text-yellow-300')
            if await win_amount_element.count() > 0:
                    win_text = await win_amount_element.text_content()
                    log_success(f"Prize: {win_text}")
                    
                    # Parse winnings (e.g., "0.00001 WBTC")
                    match = re.search(r'([\d.]+)\s+(\w+)', win_text)
                    if match:
                        amount = float(match.group(1))
                        currency = match.group(2)
                        
                        # Add to total winnings
                        if currency in total_winnings:
                            total_winnings[currency] += amount
                        else:
                            total_winnings[currency] = amount
                        
                        #  write your all balance after each win
                        log_success(f"💰 Current balance:")
                        for curr, amt in total_winnings.items():
                            log_success(f"   {curr}: {amt}")
        except Exception as e:
                log_step(f"Failed to parse winnings: {str(e)}")
        
        # Confirm transaction
        await confirm_transaction(page, shutdown_event)
    
    elif no_win_count > 0:
        losses += 1
        log_step(f"❌ Loss. Total losses: {losses}")
    else:
        log_warning("Could not determine spin result")
    
    return wins, losses


async def perform_spins(
    frame: FrameLocator, 
    page: Page, 
    total_spins: int,
    shutdown_event: asyncio.Event
) -> Dict:
    """
    Perform multiple spins and track results
    
    Args:
        frame: FrameLocator for the Monad Spin iframe
        page: Playwright page object
        total_spins: Number of spins to perform
        shutdown_event: Event to check for shutdown signal
        
    Returns:
        Dict: Statistics including wins, losses, and total winnings
    """
    log_step(f"Starting spin cycle - {total_spins} spins")

    wins = 0
    losses = 0
    total_winnings: Dict[str, float] = {}
    spin_iteration = 0
    
    try:
        for spin_iteration in range(total_spins):
            # Check for shutdown signal
            if shutdown_event.is_set():
                log_warning("⚠️  Shutdown signal received. Stopping spin cycle...")
                break
                
            log_step(f"🎰 Spin #{spin_iteration + 1}/{total_spins} | Wins: {wins} | Losses: {losses}")
            
            try:
                # Click SPIN NOW button
                spin_button = frame.locator('button:has-text("SPIN NOW")')
                await spin_button.wait_for(state='visible', timeout=10000)
                await spin_button.click()
                log_success("Clicked SPIN NOW")
                await page.wait_for_timeout(3000)
                
                # Check for shutdown signal after clicking
                if shutdown_event.is_set():
                    log_warning("⚠️  Shutdown signal received during spin. Finishing current spin...")
                
                # Process spin result
                wins, losses = await process_spin_result(frame, page, wins, losses, total_winnings, shutdown_event)
                
                # Check for shutdown signal before continuing
                if shutdown_event.is_set():
                    log_warning("⚠️  Skipping 'Spin Again' due to shutdown signal")
                    break
                
                # Click Spin Again
                spin_again = frame.locator('button:has-text("Spin Again")')
                await spin_again.wait_for(state='visible', timeout=10000)
                await spin_again.click()
                log_success("Clicked Spin Again")
                await page.wait_for_timeout(3000)
                
                # Random delay between spins (5-15 seconds)
                if not shutdown_event.is_set():
                    delay = random.randint(5, 15)
                    log_step(f"⏳ Waiting {delay}s before next spin...")
                    
                    # Split delay into smaller chunks to check shutdown flag
                    for _ in range(delay):
                        if shutdown_event.is_set():
                            log_warning("⚠️  Shutdown signal received during delay")
                            break
                        await asyncio.sleep(1)
                
            except (PlaywrightError, TargetClosedError) as e:
                if shutdown_event.is_set():
                    log_info("Spin interrupted by shutdown request")
                    break
                log_error(f"Error in iteration {spin_iteration + 1}: {str(e)}")
                break
            except Exception as e:
                log_error(f"Error in iteration {spin_iteration + 1}: {str(e)}")
                if shutdown_event.is_set():
                    log_warning("⚠️  Error occurred during shutdown. Stopping...")
                break
                
    except (PlaywrightError, TargetClosedError):
        if shutdown_event.is_set():
            log_info("Spin cycle cancelled due to shutdown")
        else:
            raise

    # Final statistics
    total_spins_completed = spin_iteration + 1 if spin_iteration > 0 or wins + losses > 0 else 0
    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    
    log_success(f"🏁 Completed! Spins: {total_spins_completed} | Wins: {wins} | Losses: {losses} | Win rate: {win_rate:.2f}%")
    
    if total_winnings:
        log_purchase("💰 Total Winnings:")
        for currency, amount in total_winnings.items():
            log_purchase(f"  {currency}: {amount}")
    
    return {
        'total_spins': total_spins_completed,
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate,
        'total_winnings': total_winnings
    }


async def safe_close_context(context: BrowserContext) -> None:
    """
    Safely close browser context with error handling
    
    Args:
        context: Browser context to close
    """
    try:
        log_step("Closing browser context...")
        await asyncio.wait_for(context.close(), timeout=5.0)
        log_success("Browser context closed successfully")
    except asyncio.TimeoutError:
        log_info("Browser context close timed out (this is normal during shutdown)")
    except (PlaywrightError, TargetClosedError):
        log_info("Browser was already closed (this is normal)")
    except Exception as e:
        # Ignore connection errors during shutdown - they're expected
        if "Connection closed" in str(e) or "Target" in str(e):
            log_info("Browser connection lost (this is normal during shutdown)")
        else:
            log_warning(f"Error while closing browser context: {str(e)}")


async def main() -> None:
    """Main execution function"""
    log_step("Starting Monad Spin bot...")
    
    # Create shutdown event for async coordination
    shutdown_event = asyncio.Event()
    
    # Setup signal handler that works with asyncio
    def signal_handler():
        log_warning("\n⚠️  Interrupt received. Initiating graceful shutdown...")
        log_info("Please wait while the bot finishes the current operation...")
        shutdown_event.set()
    
    # Get the current event loop
    loop = asyncio.get_event_loop()
    
    # Add signal handlers for Unix and Windows
    try:
        # For Unix systems (SIGINT = Ctrl+C)
        loop.add_signal_handler(
            __import__('signal').SIGINT,
            signal_handler
        )
        # For Unix systems (SIGTERM = termination signal)
        loop.add_signal_handler(
            __import__('signal').SIGTERM,
            signal_handler
        )
    except NotImplementedError:
        # Windows doesn't support add_signal_handler, use KeyboardInterrupt instead
        log_info("Running on Windows - using KeyboardInterrupt handling")
    
    # Load environment variables
    executable_path = os.getenv('COMET_EXECUTABLE_PATH')
    user_data_dir = os.getenv('COMET_USER_DATA_DIR')
    
    if not executable_path or not user_data_dir:
        log_error("Missing required environment variables: COMET_EXECUTABLE_PATH or COMET_USER_DATA_DIR")
        return
    
    log_info(f"Browser path: {executable_path}")
    log_info(f"User data directory: {user_data_dir}")
    
    context = None
    
    try:
        async with async_playwright() as p:
            log_step("Launching browser...")
            context = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir, 
                executable_path=executable_path, 
                headless=False
            )
            page = await context.new_page()
            log_success("Browser launched successfully")
            
            try:
                # Navigate to Monad Spin
                frame = await navigate_to_monad_spin(page, shutdown_event)
                
                if frame is None or shutdown_event.is_set():
                    log_warning("Shutdown requested during initial navigation")
                    return
                
                # Switch to Monad Testnet if needed
                await switch_to_monad_testnet(frame, shutdown_event)
                
                if shutdown_event.is_set():
                    return
                
                # Close modal
                await close_modal(page, shutdown_event)
                
                if shutdown_event.is_set():
                    log_warning("Shutdown requested before spin cycle")
                    return
                
                # Re-open Monad Spin
                log_step("Re-opening Monad Spin...")
                frame = await navigate_to_monad_spin(page, shutdown_event)
                
                if frame is None or shutdown_event.is_set():
                    return
                    
                await switch_to_monad_testnet(frame, shutdown_event)
                
                if shutdown_event.is_set():
                    return
                
                # Parse remaining spins
                total_spins = await parse_remaining_spins(frame)
                
                if shutdown_event.is_set():
                    return
                
                # Perform spins
                results = await perform_spins(frame, page, total_spins, shutdown_event)
                
                if shutdown_event.is_set():
                    log_warning("✋ Bot execution interrupted by user")
                else:
                    log_success("✅ Bot execution completed successfully!")
                    
                log_info(f"Final Results: {results}")
                
            except (PlaywrightError, TargetClosedError) as e:
                if shutdown_event.is_set():
                    log_info("Operation cancelled due to shutdown request")
                else:
                    log_error(f"Playwright error during execution: {str(e)}")
                    logger.exception("Full traceback:")
            except Exception as e:
                log_error(f"Fatal error during execution: {str(e)}")
                logger.exception("Full traceback:")
            
            finally:
                # Safe cleanup
                if context:
                    await safe_close_context(context)
                    
    except Exception as e:
        if not shutdown_event.is_set():
            log_error(f"Error during browser initialization: {str(e)}")
            logger.exception("Full traceback:")
    
    log_success("Program terminated gracefully")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log_success("\n✅ Program terminated by user (Ctrl+C)")
    except Exception as e:
        log_error(f"Unexpected error: {str(e)}")
        logger.exception("Full traceback:")
