package com.skinry.app.ui;


import android.app.ActionBar;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.support.v4.app.NavUtils;
import android.util.Log;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import com.flurry.android.FlurryAgent;
import com.skinry.app.R;
import com.skinry.app.custom.CustomActivity;
import com.skinry.app.utils.Const;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;

public class DisplayImageActivity extends CustomActivity {

    ArrayList<String> listNames = new ArrayList<String>();
    ArrayList<Integer> listPts = new ArrayList<Integer>();
    ArrayList<String> finalList = new ArrayList<String>();
    private Integer pos;

    public String getItem(int position)
    {
        return finalList.get(position);
    }

    Button next;
    Button prev;

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
        try {
            generateList();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        for (int i = 0; i < listPts.size(); ++i) {
            finalList.add(parseImgName(listNames.get(i)) + ", " + listPts.get(i) + " pts");
        }
        Collections.reverse(finalList);
        setContentView(R.layout.activity_display_image);
        next = (Button) findViewById(R.id.btn2);
        next.setOnClickListener(this);
        prev = (Button) findViewById(R.id.btn1);
        prev.setOnClickListener(this);
        Intent intent = getIntent();
        String message = intent.getStringExtra(History.EXTRA_MESSAGE);
        pos = new Integer(message);
        setPic();
        setBtn();
        setupActionBar();
    }

    private void setBtn() {
        prev.setClickable(true);
        next.setClickable(true);
        if (pos == 0) {
            prev.setClickable(false);
        }
        if (pos == finalList.size() - 1) {
            next.setClickable(false);
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

    @Override
    public void onClick(View v) {
        super.onClick(v);
        if (v.isEnabled()) {
            if (v.getId() == next.getId()) {
                pos++;
                setBtn();
                setPic();
                FlurryAgent.logEvent("NEXT_PHOTO_CLICKED");
            } else if (v.getId() == prev.getId()) {
                pos--;
                setBtn();
                setPic();
                FlurryAgent.logEvent("PREV_PHOTO_CLICKED");
            }
        }
    }


    private void setPic() {
        ImageView imageView = (ImageView) findViewById(R.id.imageView);
        TextView textView = (TextView) findViewById(R.id.textView1);
        String s = getItem(pos);
        Log.d("some", s);
        String[] parts = s.split(", ");
        DateFormat dateFormat = new SimpleDateFormat("yyyyMMdd_HHmmss");
        DateFormat df = new SimpleDateFormat("MM.dd.yyyy HH:mm:ss");
        Date result = null;
        try {
            result = df.parse(parts[0]);
            String name = dateFormat.format(result);
            String imageFileName = Const.JPEG_FILE_PREFIX + name + "_" + Const.JPEG_FILE_SUFFIX;
            Log.d("img", imageFileName);
            FileInputStream fis = openFileInput(imageFileName);
            Bitmap b = BitmapFactory.decodeStream(fis);
            imageView.setImageBitmap(b);
            try {
                fis.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
            Log.d("some", parts[1]);
            textView.setText(new String(parts[1].replace("pts", "%")));
        } catch (ParseException e) {
            e.printStackTrace();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
    }

    private String parseImgName(String s) {
        String date = s.substring(Const.JPEG_FILE_PREFIX.length());
        DateFormat dateFormat = new SimpleDateFormat("yyyyMMdd_HHmmss");
        DateFormat df = new SimpleDateFormat("MM.dd.yyyy HH:mm:ss"); //TODO
        try {
            Date result =  dateFormat.parse(date);
            return df.format(result);
        } catch (ParseException e) {
            e.printStackTrace();
        }
        return date;
    }

    private void generateList() throws IOException {
        String ret = "";
        InputStream inputStream = openFileInput(Const.BASE_FILE);
        if ( inputStream != null ) {
            InputStreamReader inputStreamReader = new InputStreamReader(inputStream);
            BufferedReader bufferedReader = new BufferedReader(inputStreamReader);
            String receiveString = "";
            StringBuilder stringBuilder = new StringBuilder();

            while ( (receiveString = bufferedReader.readLine()) != null ) {
                stringBuilder.append(receiveString);
            }

            inputStream.close();
            ret = stringBuilder.toString();
            String[] splitted = ret.split(" ");
            for(int i = 0; i < splitted.length; ++i) {
                if (i % 2 == 0) {
                    listNames.add(splitted[i]);
                } else {
                    listPts.add(new Integer(splitted[i]));
                }
            }
        }

    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            // Respond to the action bar's Up/Home button
            case android.R.id.home:
                NavUtils.navigateUpFromSameTask(this);
                return true;
        }
        return super.onOptionsItemSelected(item);
    }

    /*@Override
    public void onBackPressed() {
        NavUtils.navigateUpFromSameTask(this);
    }*/

}
