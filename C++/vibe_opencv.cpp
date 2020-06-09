#include <cstddef>
#include <ctime>
#include <iostream>
#include <json/json.h>

#ifndef    OPENCV_3
#include <cv.h>
#include <highgui.h>
#else
#include <opencv2/opencv.hpp>
#endif  /* OPENCV_3 */

#include <libvibe++/ViBe.h>
#include <libvibe++/distances/Manhattan.h>
#include <libvibe++/system/types.h>

using namespace std;
using namespace cv;
using namespace ViBe;

#define VIS_VID  0
#define VIS_IMG 0


int main(int argc, char** argv) {
  if (argc <  3) {
    cerr << "Usage: " << argv[0] << " video_name  json_name frames(option)" << endl;
    return EXIT_FAILURE;
  }

  int max_print_frames = -1;
  if (argc == 4) {
      max_print_frames = std::atoi(argv[3]);
  }

  /* Parameterization of ViBe. */
  typedef ViBeSequential<3, Manhattan<3> >                                ViBe;

  /* Random seed. */
  srand(time(NULL));

  cv::VideoCapture decoder(argv[1]);
  cv::Mat origin_frame;

  float scale = 1.0;
  int32_t height = (int) (scale * decoder.get(CV_CAP_PROP_FRAME_HEIGHT));
  int32_t width  = (int) (scale * decoder.get(CV_CAP_PROP_FRAME_WIDTH));

#ifdef VIS_VID
  string outputVideoPath = "./ccb_airport_mask/airport.avi";  
  cv::VideoWriter outputVideo;
  cv::Size S = cv::Size((int)width,
		        (int)height);
  double r = decoder.get(CV_CAP_PROP_FPS);
  outputVideo.open(outputVideoPath, CV_FOURCC('M', 'J', 'P', 'G'), r, S, true);
#endif

  ViBe* vibe = NULL;
  bool firstFrame = true;
  int index_frame = 1;
  cv::Mat segmentationMap(height, width, CV_8UC1);
  cv::Mat frame(height, width, CV_8UC3); 
  Json::Value res_json;
 
  while (decoder.read(origin_frame)) {
    cv::resize(origin_frame, frame, cv::Size(width, height));
    if (firstFrame) {
      /* Instantiation of ViBe. */
      vibe = new ViBe(height, width, frame.data);
      firstFrame = false;
    }

    /* Segmentation and update. */
    vibe->segmentation(frame.data, segmentationMap.data);
    vibe->update(frame.data, segmentationMap.data);

    /* Post-processing: 3x3 median filter. */
    medianBlur(segmentationMap, segmentationMap, 3);

    vector<vector<Point> > contours;
    vector<Vec4i> hierarchy;
    findContours(segmentationMap, contours, hierarchy, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE, Point(0, 0) );

    vector<Rect> boundRect(contours.size());
    vector<vector<Point> > contours_poly( contours.size() );
    for(unsigned int i = 0; i< contours.size(); i++ )
    {
	approxPolyDP( Mat(contours[i]), contours_poly[i], 3, true );
	boundRect[i] = boundingRect(Mat(contours_poly[i]) );
    }

    Json::Value frame_boxes;
    for(unsigned int i = 0; i< contours.size(); i++ )
    {
        Scalar color = Scalar(0, 0, 255);
	if (boundRect[i].area() > 50) {  
#ifdef VIS_VID 
	    rectangle(frame, boundRect[i].tl(), boundRect[i].br(), color, 2, 8, 0 );
#endif
            Json::Value box;
	    box[0] = boundRect[i].x;
	    box[1] = boundRect[i].y;
	    box[2] = boundRect[i].width;
	    box[3] = boundRect[i].height;
	    frame_boxes.append(box);
	}
    }

    res_json[std::to_string(index_frame)] = frame_boxes;
    
#ifdef VIS_VID 
    cv::Mat res_map;
    cv::cvtColor(segmentationMap, res_map, COLOR_GRAY2BGR);
    //outputVideo.write(segmentationMap);
    //outputVideo.write(res_map);
    outputVideo.write(frame);
#endif

#ifdef VIS_IMG
    cv::imwrite("./ccb_airport_mask/airport_" + std::to_string(index_frame) + ".jpg", segmentationMap);
#endif

    if (index_frame % 100 == 0) { 
    	cout << "process_frame_index: " << index_frame << endl;
    }

    index_frame += 1;
    if (index_frame > max_print_frames && max_print_frames > 0) {
	break;
    }

  }

  std::ofstream out(argv[2]);
  out << res_json;

  delete vibe;

  decoder.release();

  return EXIT_SUCCESS;
}
