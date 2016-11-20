#include <iostream>
#include <stdio.h>
#include <SDL.h>
#include <Python.h>
#include <sid.h>

#define SAMPLE_RATE   44100
#define PALCLOCKRATE  985248
#define NTSCCLOCKRATE 1022727

#define TRUE (1==1)
#define FALSE (1==0)

SDL_AudioSpec *mAudioSpec;
SID *sidchip =  new SID();

static PyObject *write_reg(PyObject *self, PyObject *args);

static PyMethodDef PythonModuleMethods[] = {
  {"write_reg",  write_reg, METH_VARARGS, "Write a SID register."},
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef PythonModule = {
   PyModuleDef_HEAD_INIT,
   "pysid",   /* name of module */
   NULL,      /* module documentation, may be NULL */
   -1,        /* size of per-interpreter state of the module,
                or -1 if the module keeps state in global variables. */
   PythonModuleMethods
};

void audio_bufferfill(short *pBuffer, int pBufferSize){
  memset( pBuffer, 0, pBufferSize );

  int samples_remain = pBufferSize / 2;

  while(samples_remain > 0){
    cycle_count cycles = samples_remain;
    int sample_count = sidchip->clock(cycles, pBuffer, samples_remain);
    samples_remain -= sample_count;
    pBuffer += sample_count;
  }
}

void audio_callback(void *userdata, uint8_t *stream, int len){
  audio_bufferfill( (short*) stream, len );
}

void audio_prepare(void) {

  SDL_AudioSpec *desired;

  desired = new SDL_AudioSpec();
  mAudioSpec = new SDL_AudioSpec();

  desired->freq=SAMPLE_RATE;
  desired->format=AUDIO_S16LSB;
  desired->channels=2;

  desired->samples=0x800;

  desired->callback = audio_callback;

  int mVal = SDL_OpenAudio(desired, mAudioSpec);

  delete desired;

  if(mVal < 0){
    std::cout << "Audio Init Failed: " << SDL_GetError() << std::endl;
  }

}

static PyObject *
write_reg(PyObject *self, PyObject *args){
  uint8_t reg = 0;
  uint8_t value = 0;

  if(!PyArg_ParseTuple(args, "bb", &reg, &value)){
      return NULL;
  }

  sidchip->write(reg, value);

    Py_RETURN_NONE;
}

void start(void){
  sidchip->set_chip_model(MOS6581);
  sidchip->set_sampling_parameters(PALCLOCKRATE, SAMPLE_INTERPOLATE, SAMPLE_RATE);
  sidchip->enable_filter(false);
  sidchip->reset();

  audio_prepare();

  SDL_PauseAudio(0);
}

void stop(void){
  SDL_PauseAudio(1);
}

PyMODINIT_FUNC
PyInit_pysid(void)
{
  PyEval_InitThreads();

  start();

  Py_AtExit(stop);
    return PyModule_Create(&PythonModule);
}
