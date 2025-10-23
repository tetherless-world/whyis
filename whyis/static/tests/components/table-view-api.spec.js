/**
 * @jest-environment jsdom
 */

import Api from '../../js/whyis_vue/components/table-view/api/api.js';

describe('table-view Api class', () => {
  test('should be an abstract class', () => {
    const api = new Api();
    expect(api).toBeInstanceOf(Api);
  });

  test('should throw EvalError when postFile is called', () => {
    const api = new Api();
    expect(() => api.postFile({})).toThrow(EvalError);
    expect(() => api.postFile({})).toThrow('Abstract');
  });

  test('should throw EvalError when getFile is called', () => {
    const api = new Api();
    expect(() => api.getFile()).toThrow(EvalError);
    expect(() => api.getFile()).toThrow('Abstract');
  });

  test('should be extendable by subclasses', () => {
    class ConcreteApi extends Api {
      postFile(file) {
        return { success: true, file };
      }
      
      getFile() {
        return { success: true, data: 'test' };
      }
    }

    const concreteApi = new ConcreteApi();
    expect(concreteApi).toBeInstanceOf(Api);
    expect(() => concreteApi.postFile({})).not.toThrow();
    expect(() => concreteApi.getFile()).not.toThrow();
    expect(concreteApi.postFile({ name: 'test.txt' })).toEqual({
      success: true,
      file: { name: 'test.txt' }
    });
  });

  test('should have postFile and getFile methods', () => {
    const api = new Api();
    expect(typeof api.postFile).toBe('function');
    expect(typeof api.getFile).toBe('function');
  });
});
