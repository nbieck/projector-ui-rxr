#include <opencv2/opencv.hpp>

using namespace cv;

int main(int argc, const char * argv[])
{
    Mat img = imread( "image.jpg" );
    imshow("", img );
    waitKey(0);

    return 0;
}