package com.skinry.app.ui;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;

import com.flurry.android.FlurryAgent;
import com.skinry.app.R;
import com.skinry.app.utils.AlbumStorageDirFactory;
import com.skinry.app.utils.BaseAlbumDirFactory;
import com.skinry.app.utils.Const;
import com.skinry.app.utils.FroyoAlbumDirFactory;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;


public class HomeActivity extends Fragment {

    private static final int ACTION_TAKE_PHOTO = 1;

    private AlbumStorageDirFactory albumStorageDirFactory = null;

    private String currentPhotoPath;
    private String lastTakenPhotoName;



	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		View v = inflater.inflate(R.layout.activity_home, null);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.FROYO) {
            albumStorageDirFactory = new FroyoAlbumDirFactory();
        } else {
            albumStorageDirFactory = new BaseAlbumDirFactory();
        }
		setupView(v);
		return v;
	}

	private void setupView(View v) {
		final View sw = v.findViewById(R.id.take_photo_button);
		sw.setOnClickListener(new OnClickListener() {

			@Override
			public void onClick(View v) {
                FlurryAgent.logEvent("HOME_TAKE_CLICKED");
                startCamera();
			}
		});
	}

    private void startCamera() {
        Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        File f = null;
        try {
            f = setUpPhotoFile();
            currentPhotoPath = f.getAbsolutePath();
            takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, Uri.fromFile(f));
        } catch (IOException e) {
            e.printStackTrace();
            f = null;
            currentPhotoPath = null;
            //TODO TOAST
        }
        startActivityForResult(takePictureIntent, ACTION_TAKE_PHOTO);
    }

    private File setUpPhotoFile() throws IOException {

        File f = createImageFile();
        currentPhotoPath = f.getAbsolutePath();

        return f;
    }

    private File createImageFile() throws IOException {
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        String imageFileName = Const.JPEG_FILE_PREFIX + timeStamp + "_";
        lastTakenPhotoName = imageFileName;
        File albumF = getAlbumDir();
        File imageF = File.createTempFile(imageFileName, Const.JPEG_FILE_SUFFIX, albumF);
        return imageF;
    }

    private File getAlbumDir() {
        File storageDir = null;

        if (Environment.MEDIA_MOUNTED.equals(Environment.getExternalStorageState())) {
            storageDir = albumStorageDirFactory.getAlbumStorageDir(Const.ALBUM_NAME);

            if (storageDir != null) {
                if (! storageDir.mkdirs()) {
                    if (! storageDir.exists()){
                        Log.d("Skinry", "failed to create directory");
                        return null;
                    }
                }
            }

        } else {
            Log.v(getString(R.string.app_name), "External storage is not mounted READ/WRITE.");
        }
        return storageDir;
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (resultCode == Activity.RESULT_OK) {
            switch (requestCode) {
                case ACTION_TAKE_PHOTO: {
                    if (resultCode == Activity.RESULT_OK) {
                        Intent intent = new Intent(getActivity(), PhotoActivity.class);
                        intent.putExtra(Const.EXTRA_PATH_MESSAGE, currentPhotoPath + ' ' + lastTakenPhotoName);
                        startActivity(intent);
                    }
                    break;
                }
            }
        }
    }

    @Override
    public void onPause() {
        super.onPause();
        Log.d("kmp", "this");
    }

}
