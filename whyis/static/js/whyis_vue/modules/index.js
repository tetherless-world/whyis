/**
 * Module exports for shared functionality across the Whyis Vue application.
 * Provides centralized access to event services and utility modules.
 * 
 * @module modules
 */

import EventServices from  './events/event-services';
import Slug from './slugs';

/**
 * Exported modules available throughout the application
 * @namespace
 * @property {Object} EventServices - Event handling and navigation services
 * @property {Object} Slug - String manipulation utilities for URL-safe identifiers
 */
export {
    EventServices,
    Slug,
}
