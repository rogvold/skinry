package com.skinry.app.ui;

import android.app.ActionBar;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Point;
import android.graphics.drawable.BitmapDrawable;
import android.media.FaceDetector;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.v4.app.NavUtils;
import android.util.Base64;
import android.util.Log;
import android.view.Display;
import android.view.Gravity;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.flurry.android.FlurryAgent;
import com.skinry.app.R;
import com.skinry.app.custom.CustomActivity;
import com.skinry.app.utils.AlbumStorageDirFactory;
import com.skinry.app.utils.BaseAlbumDirFactory;
import com.skinry.app.utils.Const;
import com.skinry.app.utils.FroyoAlbumDirFactory;

import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.util.EntityUtils;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.Random;

public class PhotoActivity extends CustomActivity {

    private String currentPhotoPath;
    private ImageView imageView;

    private static final int ACTION_TAKE_PHOTO = 1;

    private AlbumStorageDirFactory albumStorageDirFactory = null;

    private String lastTakenPhotoName;
    private boolean isSent = false;
    AlertDialog adviceDialog = null;

    public void onAdClick(View view) {
        Log.d("new", "this");
        Intent intent = new Intent(this, AdsActivity.class);
        startActivity(intent);
    }

    public enum UIModes {SEND, ANALYZED, ANOTHER}
    UIModes curMode;


    private int points = 90;


    Boolean saved = false;

    @Override
    protected void onStart() {
        super.onStart();
        FlurryAgent.onStartSession(this, Const.FLURRY_API_KEY);
    }

    @Override
    protected void onStop() {
        super.onStop();
        FlurryAgent.onEndSession(this);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_photo);

        Intent intent = getIntent();
        currentPhotoPath = intent.getStringExtra(Const.EXTRA_PATH_MESSAGE);
        String[] some = currentPhotoPath.split(" ");//TODO may cause problems
        lastTakenPhotoName = some[1];
        Log.d("some", lastTakenPhotoName);
        currentPhotoPath = some[0];
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.FROYO) {
            albumStorageDirFactory = new FroyoAlbumDirFactory();
        } else {
            albumStorageDirFactory = new BaseAlbumDirFactory();
        }
        setupActionBar();
        initButtons();
        setPic();
        galleryAddPic();
        setUI(UIModes.SEND);
    }


    //TODO ERROR HANDLER


    public boolean isOnline() {
        ConnectivityManager cm =
                (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo netInfo = cm.getActiveNetworkInfo();
        if (netInfo != null && netInfo.isConnectedOrConnecting()) {
            return true;
        }
        return false;
    }

    private void setUI(UIModes mode) {
        curMode = mode;
        TextView t;
        ((Button)findViewById(R.id.ads_btn)).setText(R.string.ads_title);
        //((Button)findViewById(R.id.ads)).setClickable(true);
        switch (curMode) {
            case SEND:
                ((Button)findViewById(R.id.btn2)).setText(R.string.ok);
                ((Button)findViewById(R.id.btn1)).setText(R.string.retake_photo);
                //((Button)findViewById(R.id.ads)).setText(R.string.empty_string);
                //((Button)findViewById(R.id.ads)).setClickable(false);
                findViewById(R.id.textView1).setVisibility(View.INVISIBLE);
                findViewById(R.id.ads_layout).setVisibility(View.INVISIBLE);
                findViewById(R.id.ads_btn).setClickable(false);
                break;
            case ANALYZED:
                ((Button)findViewById(R.id.btn2)).setText(R.string.save_button);
                ((Button)findViewById(R.id.btn1)).setText(R.string.retake_photo);
                //((Button)findViewById(R.id.ads)).setText(R.string.ads_title);
                //((Button)findViewById(R.id.ads)).setClickable(true);
                t = ((TextView)findViewById(R.id.textView1));
                t.setVisibility(View.VISIBLE);
                t.setText(getString(R.string.clear_skin_is) + " " + points + "%");
                if (Locale.getDefault().toString().equals("ru_RU")) {
                    findViewById(R.id.ads_layout).setVisibility(View.VISIBLE);
                    findViewById(R.id.ads_btn).setClickable(true);
                }
                break;
            case ANOTHER:
                //((Button)findViewById(R.id.ads)).setText(R.string.empty_string);
                ((Button)findViewById(R.id.btn2)).setText(R.string.ok);
                ((Button)findViewById(R.id.btn1)).setText(R.string.retake_photo);
                //((Button)findViewById(R.id.ads)).setClickable(false);
                findViewById(R.id.textView1).setVisibility(View.INVISIBLE);
                findViewById(R.id.ads_layout).setVisibility(View.INVISIBLE);
                findViewById(R.id.ads_btn).setClickable(false);
                break;
        }
    }

    private void initButtons() {
        findViewById(R.id.btn1).setOnClickListener(this);
        findViewById(R.id.btn2).setOnClickListener(this);
    }

    @Override
    public void onClick(View v)
    {
        super.onClick(v);
        if (v.getId() == R.id.btn1) {
            saved = false;
            startCamera();
            switch (curMode) {
                case SEND:
                    FlurryAgent.logEvent("SELF_RETAKE_CLICKED");
                    break;
                case ANALYZED:
                    FlurryAgent.logEvent("AFTER_RETAKE_CLICKED");
                case ANOTHER:
                    FlurryAgent.logEvent("BAD_RETAKE_CLICKED");
            }
        } else if (v.getId() == R.id.btn2) {
            switch (curMode) {
                case SEND:
                    FlurryAgent.logEvent("SEND_CLICKED");
                    //TODO check connection
                    if (!isOnline()) {
                        showCriticalErrorDialog(R.string.no_internet);
                        return;
                    }
                    isSent = true;
                    ServerHandler sh = new ServerHandler();
                    sh.execute();
                    break;
                case ANALYZED:
                    FlurryAgent.logEvent("SAVE_CLICKED");
                    if (imageView.getDrawable() != null) {
                        try {
                            if (!saved) {
                                saveInnerImageFile(((BitmapDrawable) imageView.getDrawable()).getBitmap());
                                savePts(points);
                                Context context = getApplicationContext();
                                CharSequence text = getString(R.string.saved);
                                int duration = Toast.LENGTH_SHORT;
                                Toast toast = Toast.makeText(context, text, duration);
                                toast.setGravity(Gravity.CENTER_VERTICAL, 0, 0);
                                toast.show();
                                saved = true;
                            }
                        } catch (IOException e) {
                            showCriticalErrorDialog(R.string.save_error);
                            e.printStackTrace();
                        }
                    }
                    break;
                case ANOTHER:
                    FlurryAgent.logEvent("ERROR_OK_CLICKED");
                    finish();
                    break;
            }
        }

    }

    protected void setupActionBar() {
        final ActionBar actionBar = getActionBar();
        actionBar.setDisplayShowTitleEnabled(true);
        actionBar.setNavigationMode(ActionBar.NAVIGATION_MODE_STANDARD);
        actionBar.setDisplayUseLogoEnabled(true);
        actionBar.setLogo(R.drawable.icon);
        actionBar.setDisplayHomeAsUpEnabled(true);
        actionBar.setHomeButtonEnabled(true);
    }

    private void setPic() {

        imageView = (ImageView) findViewById(R.id.imageView);

        Display display = getWindowManager().getDefaultDisplay();
        Point size = new Point();
        display.getSize(size);
        int width = size.x;

		/* There isn't enough memory to open up more than a couple camera photos */
		/* So pre-scale the target bitmap into which the file is decoded */

		/* Get the size of the image */
        BitmapFactory.Options bmOptions = new BitmapFactory.Options();
        bmOptions.inJustDecodeBounds = true;
        BitmapFactory.decodeFile(currentPhotoPath, bmOptions);
        int photoW = bmOptions.outWidth;

		/* Figure out which way needs to be reduced less */
        int scaleFactor = photoW/width;

		/* Set bitmap options to scale the image decode target */
        bmOptions.inJustDecodeBounds = false;
        bmOptions.inSampleSize = scaleFactor;
        bmOptions.inPurgeable = true;

		/* Decode the JPEG file into a Bitmap */
        Bitmap bitmap = BitmapFactory.decodeFile(currentPhotoPath, bmOptions);

		/* Associate the Bitmap to the ImageView */
        imageView.setImageBitmap(bitmap);
        imageView.setVisibility(View.VISIBLE);
        FaceDetectionHandler fdh = new FaceDetectionHandler();
        fdh.execute();
    }

    private void galleryAddPic() {
        Intent mediaScanIntent = new Intent("android.intent.action.MEDIA_SCANNER_SCAN_FILE");
        File f = new File(currentPhotoPath);
        Uri contentUri = Uri.fromFile(f);
        mediaScanIntent.setData(contentUri);
        this.sendBroadcast(mediaScanIntent);
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
        setUI(UIModes.SEND);
        if (resultCode == Activity.RESULT_OK) {
            switch (requestCode) {
                case ACTION_TAKE_PHOTO: {
                    if (resultCode == Activity.RESULT_OK) {
                        setPic();
                        galleryAddPic();
                    }
                    break;
                }
            }
        }
    }

    class ServerHandler extends AsyncTask<Void, Void, Void> {

        Bitmap imageBitmap;

        int resCode;

        boolean okay;

        String message = "";

        ByteArrayOutputStream baos = new ByteArrayOutputStream();

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            showAdviceDialog();
        }


        @Override
        protected Void doInBackground(Void... params) {
            okay = false;
            HttpPost request = new HttpPost(Const.API_SEND_URL);
            request.setHeader("Content-type", "application/json");
            FileInputStream fis = null;
            try {
                fis = openFileInput(Const.TMP_IMAGE_FILE_NAME);
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            }
            Log.d("dbg", ":D");
            Bitmap bitmap = BitmapFactory.decodeStream(fis);
            bitmap.compress(Bitmap.CompressFormat.JPEG, 100, baos);
            try {
                byte[] b = baos.toByteArray();
                String encodedImage = Base64.encodeToString(b, Base64.DEFAULT);
                JSONObject img = new JSONObject();
                img.put("img", encodedImage);
                Log.d("dbg", "D:");

                StringEntity entity = new StringEntity(img.toString());
                request.setEntity(entity);
                DefaultHttpClient httpClient = new DefaultHttpClient();

                Log.d("dbg", "sended");
                HttpResponse response = httpClient.execute(request);
                resCode = response.getStatusLine().getStatusCode();
                Log.d("dbg", "ok");
                if (resCode == 201) {
                    okay = true;
                    String responseText = null;
                    responseText = EntityUtils.toString(response.getEntity());
                    JSONObject json = new JSONObject(responseText);
                    String p_filename = json.getString("p_name");
                    response = null;
                    HttpGet getRequest = new HttpGet(Const.API_POST_PROC_URL + p_filename);
                    response = httpClient.execute(getRequest);
                    responseText = EntityUtils.toString(response.getEntity());
                    json = new JSONObject(responseText);
                    encodedImage = json.getString("img");
                    int pts = json.getInt("pts");
                    byte[] decodedString = Base64.decode(encodedImage, Base64.DEFAULT);
                    imageBitmap = BitmapFactory.decodeByteArray(decodedString, 0, decodedString.length);
                    points = pts;
                    //saveInnerImageFile(imageBitmap);
                    //savePts(pts);
                } else {
                    String responseText = null;
                    responseText = EntityUtils.toString(response.getEntity());
                    JSONObject json = new JSONObject(responseText);
                    Log.d("Server error", json.getString("error"));
                    message = json.getString("error");
                }
            }catch (Exception e) {
                Log.d("exception_server", e.toString());
            }
            return null;
        }

        @Override
        protected void onPostExecute(Void result) {
            super.onPostExecute(result);
            if (adviceDialog != null) {
                adviceDialog.getButton(DialogInterface.BUTTON_POSITIVE).setEnabled(true);
                adviceDialog.setTitle(R.string.photo_proc);
            }
            if (okay) {
                Display display = getWindowManager().getDefaultDisplay();
                Point size = new Point();
                display.getSize(size);
                int height = size.y;
                int photoHeight = imageBitmap.getHeight();
                int scaleFactor = height/photoHeight;
                if (scaleFactor > 2) {
                    scaleFactor -= 1;
                }
                imageView.setImageBitmap(Bitmap.createScaledBitmap(imageBitmap,
                        scaleFactor*imageBitmap.getWidth(), scaleFactor*imageBitmap.getHeight(),
                        false));
                setUI(UIModes.ANALYZED);
            } else {
                if (message.equals(Const.ERROR_NO_FACE)) {
                    showErrorDialog(R.string.error_no_face);

                } else if (message.equals(Const.ERROR_SMALL_FACE)) {
                    showErrorDialog(R.string.error_small_face);

                } else {
                    if (isFinishing())
                        showCriticalErrorDialog(R.string.critical_error);
                }
                setUI(UIModes.ANOTHER);
            }

        }
    }

    private void saveInnerImageFile(Bitmap imageBitmap) throws IOException {
        String fileName = lastTakenPhotoName + Const.JPEG_FILE_SUFFIX;

        FileOutputStream fos = openFileOutput(fileName, Context.MODE_PRIVATE);
        imageBitmap.compress(Bitmap.CompressFormat.JPEG, 100, fos);
        fos.close();
        return ;
    }

    private void savePts(int pts) throws IOException {
        String fileName = Const.BASE_FILE;
        FileOutputStream f = openFileOutput(fileName, Context.MODE_APPEND);
        OutputStreamWriter outputStreamWriter = new OutputStreamWriter(f);
        outputStreamWriter.write(lastTakenPhotoName + " ");
        Integer i = new Integer(pts);
        outputStreamWriter.write(i.toString() + " ");
        Log.d("SAVING", lastTakenPhotoName/*.split(".")[0]*/);
        outputStreamWriter.close();
        f.close();
    }


    class FaceDetectionHandler extends AsyncTask<Void, Void, Void> {

        private static final int MAX_FACES = 2;
        private Bitmap image;
        private FaceDetector.Face[] faces;
        private int face_count;


        @Override
        protected void onPreExecute() {
            FileOutputStream fos = null;
            try {
                fos = openFileOutput(Const.TMP_IMAGE_FILE_NAME, Context.MODE_PRIVATE);
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            }
            //imageBitmap.compress(Bitmap.CompressFormat.JPEG, 100, fos);
            if(fos != null) {
                Bitmap imageBitmap = ((BitmapDrawable) imageView.getDrawable()).getBitmap();
                imageBitmap.compress(Bitmap.CompressFormat.JPEG, 100, fos);
                try {
                    fos.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }

        @Override
        protected Void doInBackground(Void... params) {
            FileInputStream fis = null;
            try {
                fis = openFileInput(Const.TMP_IMAGE_FILE_NAME);
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            }
            Log.d("LOL", "sdd");
            BitmapFactory.Options bitmap_options = new BitmapFactory.Options();
            bitmap_options.inPreferredConfig = Bitmap.Config.RGB_565;
            image = BitmapFactory.decodeStream(fis, null, bitmap_options);
            Log.d("LOL", ":D");
            FaceDetector face_detector = new FaceDetector(image.getWidth(), image.getHeight(), MAX_FACES);
            faces = new FaceDetector.Face[MAX_FACES];
            face_count = face_detector.findFaces(image, faces);
            Log.d("Face_Detection", "Face Count: " + String.valueOf(face_count));
            return null;
        }

        @Override
        protected void onPostExecute(Void result) {
            if (!isSent && face_count != 1) {
                showSuggestionDialog();
            }
        }

    }

    private void showErrorDialog(int messageId) {
        new AlertDialog.Builder(this)
                .setTitle(R.string.error)
                .setMessage(messageId)
                .setPositiveButton(R.string.retake_photo, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        startCamera();
                    }
                })
                .setNegativeButton(R.string.cancel, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        finish();
                    }
                })
                .show();
    }

    private void showCriticalErrorDialog(int messageId) {
        new AlertDialog.Builder(this)
                .setTitle(R.string.error)
                .setMessage(messageId)
                .setPositiveButton(R.string.ok, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        finish();
                    }
                })
                .show();
    }

    private void showSuggestionDialog() {
        new AlertDialog.Builder(this)
                .setTitle(R.string.attention)
                .setMessage(R.string.dialog_unacceptable_photo)
                .setPositiveButton(R.string.retake_photo, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        startCamera();
                    }
                })
                .setNegativeButton(R.string.cancel, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                    }
                })
                .show();
    }

    private void showAdviceDialog() {
        Random randomGenerator = new Random();
        AlertDialog.Builder ad =  new AlertDialog.Builder(this);
        ad.setTitle(R.string.while_processing);
        if (Locale.getDefault().toString().equals("ru_RU")) {
            ad.setMessage(Const.ADVICES[randomGenerator.nextInt(Const.ADVICES.length)]);
        }
        ad.setPositiveButton(R.string.ok, new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int which) {
            }
        });
        adviceDialog = ad.create();
        adviceDialog.show();
        adviceDialog.getButton(DialogInterface.BUTTON_POSITIVE).setEnabled(false);
        adviceDialog.setCanceledOnTouchOutside(false);
    }


    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case android.R.id.home:
                NavUtils.navigateUpFromSameTask(this);
                return true;
        }
        return super.onOptionsItemSelected(item);
    }

    @Override
    public void onBackPressed() {
        NavUtils.navigateUpFromSameTask(this);
    }
}
