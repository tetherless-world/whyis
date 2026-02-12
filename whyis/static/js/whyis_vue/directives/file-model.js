/**
 * Vue directive for file input handling with format detection
 * Reads file content and detects format based on file extension
 * Migrated from Angular directive "fileModel"
 * 
 * Usage:
 * <input type="file" v-file-model="{ content: fileContent, format: fileFormat }" />
 * 
 * @module file-model
 */

import { getFormatFromFilename } from '../utilities/formats';
import { decodeDataURI } from '../utilities/url-utils';

export default {
  bind(el, binding, vnode) {
    el.addEventListener('change', function(changeEvent) {
      if (!changeEvent.target.files || changeEvent.target.files.length === 0) {
        return;
      }

      const file = changeEvent.target.files[0];
      const reader = new FileReader();
      
      // Detect format from filename
      const formatInfo = getFormatFromFilename(file.name);
      
      reader.onload = function(loadEvent) {
        const decodedData = decodeDataURI(loadEvent.target.result);
        
        // Update the bound value object
        if (binding.value && typeof binding.value === 'object') {
          if (binding.value.content !== undefined) {
            binding.value.content = decodedData.value;
          }
          if (binding.value.format !== undefined && formatInfo) {
            binding.value.format = formatInfo.mimetype;
          }
        }
        
        // Emit event for Vue component reactivity
        if (vnode.componentInstance) {
          vnode.componentInstance.$emit('file-loaded', {
            content: decodedData.value,
            format: formatInfo ? formatInfo.mimetype : null,
            filename: file.name
          });
        }
      };
      
      reader.onerror = function(error) {
        console.error('Error reading file:', error);
        if (vnode.componentInstance) {
          vnode.componentInstance.$emit('file-error', error);
        }
      };
      
      reader.readAsDataURL(file);
    });
  },
  
  unbind(el) {
    // Clean up event listeners
    el.removeEventListener('change', null);
  }
};
