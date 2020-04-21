package main

import (
	"bytes"
	"image"
	"image/png"
	"os"

	"github.com/kbinani/screenshot"
)

func main() {
	//Capture screen
	n := screenshot.NumActiveDisplays()

	for i := 0; i < n; i++ {
		bounds := screenshot.GetDisplayBounds(i)

		img, err := screenshot.CaptureRect(bounds)
		if err != nil {
			panic(err)
		}
		//Create a buffer of this image as string
		buf := new(bytes.Buffer)
		var image2 image.Image
		png.Encode(buf, img)
		var stringe string
		//Convert this buffer to Image again
		buffer := buf.Bytes()
		image2, stringe, nil := image.Decode(bytes.NewReader(buffer))
		//Save the image to disk
		f, err := os.Create("outimage." + stringe)
		if err != nil {
			// Handle error
		}
		defer f.Close()
		err = png.Encode(f, image2)
		if err != nil {
			// Handle error
		}

	}
}
