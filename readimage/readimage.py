import usage
import readimage.nef
import readimage.classic
import readimage.ser
import readimage.yuv
import readimage.video

commands = {
	"nef"   : (readimage.nef.run, "read Nikon NEF"),
	"classic"  : (readimage.classic.run, "read usual images (JPG, PNG, TIFF)"),
	"ser" : (readimage.ser.run, "read SER"),
	"yuv" : (readimage.yuv.run, "read YUV images"),
	"video" : (readimage.video.run, "read VIDEO images"),
}

def run(argv):
	usage.run(argv, "readimage", commands, autohelp=True)
