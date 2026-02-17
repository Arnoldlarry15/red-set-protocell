/**
 * Image Optimization Utilities
 * Handles lazy loading, blur-up effects, and responsive images
 */

interface ImageState {
  isLoading: boolean;
  isLoaded: boolean;
  hasError: boolean;
}

/**
 * Preload an image and return a promise
 * Useful for ensuring images are loaded before rendering
 */
export function preloadImage(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.src = src;
    img.onload = () => resolve();
    img.onerror = () => reject(new Error(`Failed to load image: ${src}`));
  });
}

/**
 * Batch preload multiple images
 */
export async function preloadImages(sources: string[]): Promise<void> {
  const promises = sources.map(src => preloadImage(src));
  await Promise.all(promises);
}

/**
 * Get blur placeholder data URL
 * Creates a solid color placeholder while image loads
 */
export function getBlurPlaceholder(color: string = '#1a1a1a'): string {
  const canvas = document.createElement('canvas');
  canvas.width = 1;
  canvas.height = 1;
  const ctx = canvas.getContext('2d');
  if (ctx) {
    ctx.fillStyle = color;
    ctx.fillRect(0, 0, 1, 1);
  }
  return canvas.toDataURL();
}

/**
 * Optimized image component props generator
 * Returns all necessary props for lazy loading
 */
export interface OptimizedImageProps {
  src: string;
  alt: string;
  className?: string;
  loading?: 'lazy' | 'eager';
  decoding?: 'async' | 'auto';
  sizes?: string;
  srcSet?: string;
  onLoad?: () => void;
  onError?: () => void;
}

export function getOptimizedImageProps(
  src: string,
  alt: string,
  options: Partial<OptimizedImageProps> = {}
): OptimizedImageProps {
  return {
    src,
    alt,
    loading: 'lazy',
    decoding: 'async',
    ...options,
  };
}

/**
 * Generate srcset for responsive images
 * CDN images already have width/height parameters
 */
export function generateResponsiveSrcSet(baseUrl: string): string {
  // If using CDN with width parameters, generate multiple sizes
  if (baseUrl.includes('width=')) {
    // Extract base and modify width
    const widths = ['800', '1200', '1600'];
    return widths.map(w => {
      const url = baseUrl.replace(/width=\d+/i, `width=${w}`);
      return `${url} ${w}w`;
    }).join(', ');
  }
  return baseUrl;
}

/**
 * Get image loading strategy based on viewport
 */
export function getImageLoadingStrategy(threshold: number = 0.1): IntersectionObserverInit {
  return {
    root: null,
    rootMargin: '50px',
    threshold: threshold,
  };
}

/**
 * Compress image URL for optimal delivery
 * Adjusts quality and format for web delivery
 */
export function optimizeImageUrl(
  url: string,
  options: {
    format?: 'webp' | 'jpg' | 'png';
    quality?: number;
    maxWidth?: number;
  } = {}
): string {
  const { format = 'webp', quality = 85, maxWidth = 1200 } = options;

  // For CDN URLs with format parameter, update them
  if (url.includes('format=')) {
    let optimized = url.replace(/format=\w+/i, `format=${format}`);
    if (quality && url.includes('quality=')) {
      optimized = optimized.replace(/quality=\d+/i, `quality=${quality}`);
    }
    if (maxWidth && url.includes('width=')) {
      // Don't override if already set to smaller value
      const match = url.match(/width=(\d+)/);
      if (match && parseInt(match[1]) > maxWidth) {
        optimized = optimized.replace(/width=\d+/i, `width=${maxWidth}`);
      }
    }
    return optimized;
  }

  return url;
}

/**
 * Create a blur-up image loading effect
 * Use with a low-res placeholder image
 */
export class BlurUpImage {
  private img: HTMLImageElement;
  private canvas: HTMLCanvasElement | null = null;

  constructor(imgElement: HTMLImageElement) {
    this.img = imgElement;
  }

  /**
   * Initialize blur-up effect with a low-res placeholder
   */
  initializeWithPlaceholder(lowResUrl: string): Promise<void> {
    return new Promise((resolve) => {
      const lowRes = new Image();
      lowRes.src = lowResUrl;
      lowRes.onload = () => {
        this.drawBlurredImage(lowRes);
        // Now load the full-res image
        this.img.src = this.img.dataset.src || lowResUrl;
        this.img.onload = () => resolve();
      };
      lowRes.onerror = () => resolve(); // Continue even if placeholder fails
    });
  }

  /**
   * Draw a blurred version of the placeholder
   */
  private drawBlurredImage(img: HTMLImageElement): void {
    if (!this.canvas) {
      this.canvas = document.createElement('canvas');
      this.canvas.width = img.width;
      this.canvas.height = img.height;
    }

    const ctx = this.canvas.getContext('2d');
    if (!ctx) return;

    // Draw the image
    ctx.drawImage(img, 0, 0);

    // Apply blur effect
    ctx.filter = 'blur(10px)';
    ctx.drawImage(this.canvas, 0, 0);

    // Set as background
    const blurDataUrl = this.canvas.toDataURL();
    this.img.style.backgroundImage = `url(${blurDataUrl})`;
    this.img.style.backgroundSize = 'cover';
  }
}

/**
 * Intersection Observer for lazy loading
 * Used by components to trigger image loading on scroll
 */
export function createLazyLoadObserver(
  callback: (entries: IntersectionObserverEntry[]) => void
): IntersectionObserver {
  const options: IntersectionObserverInit = {
    root: null,
    rootMargin: '50px',
    threshold: 0.01,
  };

  return new IntersectionObserver(callback, options);
}

/**
 * Utility to track image load state
 */
export function useImageLoadState(src: string): ImageState {
  return {
    isLoading: true,
    isLoaded: false,
    hasError: false,
  };
}

/**
 * Get image alt text for accessibility
 */
export function getAccessibleAltText(imageName: string): string {
  const altTexts: { [key: string]: string } = {
    // Architecture images
    'feedbackLoop': 'Evolving Feedback Loop - Adaptive system for continuous ethical testing',
    'eggHero': 'EGG - Ethical Guardrail Governor ensuring compliance and moral integrity',
    'sniperSpotter': 'Sniper/Spotter Dual Agent Cell for precision threat elimination',
    'digitalEye': 'Digital eye with circuit board overlay representing system awareness',
    'redSetProtocol': 'Red Set Protocol - Next generation AI red teaming security suite',
    'redSetProtoCell': 'Red Set ProtoCell - Autonomous AI red teaming with ethical guardrails',
    
    // Technical diagrams
    'systemArchitecture': 'System architecture diagram showing interconnected components',
    'networkVisualization': 'Network visualization with glowing nodes and connections',
    'circuitBoard': 'Circuit board pattern representing digital infrastructure',
    'dataFlow': 'Data flow visualization with streaming information',
    
    // Default fallback
    'default': 'System visualization image',
  };

  return altTexts[imageName] || altTexts['default'];
}

/**
 * Check if browser supports WebP format
 */
export async function supportsWebP(): Promise<boolean> {
  return new Promise((resolve) => {
    const webP = new Image();
    webP.onload = webP.onerror = () => {
      resolve(webP.height === 2);
    };
    webP.src = 'data:image/webp;base64,UklGRjoIAABXEBP8AAAASUVORK5CYII=';
  });
}

/**
 * Performance metric for image loading
 */
export interface ImageLoadMetrics {
  startTime: number;
  endTime?: number;
  duration?: number;
  size?: number;
  success: boolean;
}

export class ImageLoadMetricsTracker {
  private metrics: Map<string, ImageLoadMetrics> = new Map();

  startTracking(imageId: string): void {
    this.metrics.set(imageId, {
      startTime: performance.now(),
      success: false,
    });
  }

  endTracking(imageId: string, success: boolean = true): void {
    const metric = this.metrics.get(imageId);
    if (metric) {
      metric.endTime = performance.now();
      metric.duration = metric.endTime - metric.startTime;
      metric.success = success;
    }
  }

  getMetrics(imageId: string): ImageLoadMetrics | undefined {
    return this.metrics.get(imageId);
  }

  getAllMetrics(): ImageLoadMetrics[] {
    return Array.from(this.metrics.values());
  }

  getAverageLoadTime(): number {
    const metrics = this.getAllMetrics();
    if (metrics.length === 0) return 0;
    const total = metrics.reduce((sum, m) => sum + (m.duration || 0), 0);
    return total / metrics.length;
  }
}
