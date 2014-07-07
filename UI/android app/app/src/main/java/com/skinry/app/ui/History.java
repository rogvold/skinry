package com.skinry.app.ui;

import android.app.AlertDialog;
import android.content.ContentResolver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.media.ThumbnailUtils;
import android.os.Bundle;
import android.provider.MediaStore;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.BaseAdapter;
import android.widget.ImageView;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.TextView;

import com.flurry.android.FlurryAgent;
import com.skinry.app.R;
import com.skinry.app.utils.Const;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;

// TODO: Auto-generated Javadoc
/**
 * The Class History is a Fragment that is displayed in the Main activity when
 * the user taps on History tab or when user swipes to Fourth page in ViewPager.
 * You can customize this fragment's contents as per your need.
 */
public class History extends Fragment
{


    public final static String EXTRA_MESSAGE = "com.skinry.app.MESSAGE";

    ArrayList<String> listNames = new ArrayList<String>();
    ArrayList<Integer> listPts = new ArrayList<Integer>();
    ArrayList<String> finalList;

    ListView list;


	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState)
	{
        Log.d("history kmp", "creating view");
		View v = inflater.inflate(R.layout.listview, null);

		setupView(v);
		return v;
	}

	/**
	 * Setup the view components for this fragment. You write your code for
	 * initializing the views, setting the adapters, touch and click listeners
	 * etc.
	 * 
	 * @param v
	 *            the base view of fragment
	 */
	private void setupView(View v)
	{
        list = (ListView) v;
        try {
            generateList();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        list.setAdapter(null);
        finalList = new ArrayList<String>();
        for (int i = 0; i < listPts.size(); ++i) {
            String s = parseImgName(listNames.get(i)) + ", " + listPts.get(i) + " pts";
            if (finalList.indexOf(s) == -1) {
                finalList.add(s);
            }
        }
        Collections.reverse(finalList);
        if (list.getAdapter() == null) {
            list.setAdapter(new HistoryAdapter(getActivity(), finalList));
            list.setOnItemClickListener(new AdapterView.OnItemClickListener() {
                @Override
                public void onItemClick(AdapterView<?> parent, View itemClicked, int position,
                                        long id) {

                    FlurryAgent.logEvent("HISTORY_ITEM_CLICKED");
                    String message = new Integer(position).toString();
                    Intent intent = new Intent(getActivity(), DisplayImageActivity.class);
                    intent.putExtra(EXTRA_MESSAGE, message);
                    startActivity(intent);
                }
            });
        } else {
            //((BaseAdapter)list.getAdapter()).notifyDataSetChanged();
        }
	}

	/**
	 * The Class HistoryAdapter is the adapter for list view used in this
	 * fragment. You must provide valid values for adapter count and must write
	 * your code for binding the data to each item in adapter as per your need.
	 */
	private class HistoryAdapter extends BaseAdapter
	{
        Context ctx;
        LayoutInflater lInflater;
        ArrayList<String> objects;

        HistoryAdapter(Context context, ArrayList<String> products) {
            ctx = context;
            objects = products;
            lInflater = (LayoutInflater) ctx.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        }

		/* (non-Javadoc)
		 * @see android.widget.Adapter#getCount()
		 */
		@Override
		public int getCount()
		{
			return objects.size();
		}

		/* (non-Javadoc)
		 * @see android.widget.Adapter#getItem(int)
		 */
		@Override
		public Object getItem(int position)
		{
			return objects.get(position);
		}

		/* (non-Javadoc)
		 * @see android.widget.Adapter#getItemId(int)
		 */
		@Override
		public long getItemId(int arg0)
		{
			return arg0;
		}

		/* (non-Javadoc)
		 * @see android.widget.Adapter#getView(int, android.view.View, android.view.ViewGroup)
		 */
		@Override
		public View getView(int position, View convertView, ViewGroup parent)
		{
            View view = convertView;
            if (view == null) {
                view = lInflater.inflate(R.layout.history_item, parent, false);
            }
            String s = (String) getItem(position);
            String[] parts = s.split(",");
            DateFormat dateFormat = new SimpleDateFormat("yyyyMMdd_HHmmss");
            DateFormat df = new SimpleDateFormat("MM.dd.yyyy HH:mm:ss");
            Date result = null;
            try {
                result = df.parse(parts[0]);
                String name = dateFormat.format(result);
                String imageFileName = Const.JPEG_FILE_PREFIX + name + "_" + Const.JPEG_FILE_SUFFIX;
                Log.d("img", imageFileName);
                FileInputStream fis = getActivity().openFileInput(imageFileName);
                Bitmap ThumbImage = ThumbnailUtils.extractThumbnail(BitmapFactory.decodeStream(fis),
                        Const.THUMBNAIL_SIZE, Const.THUMBNAIL_SIZE);
                try {
                    fis.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
                ((TextView) view.findViewById(R.id.textViewDate)).setText(parts[0]);
                ((TextView) view.findViewById(R.id.textViewDown)).setText(parts[1].replace("pts", "%"));
                ((ProgressBar)view.findViewById(R.id.progressBar)).setProgress(new Integer(parts[1].split(" ")[1]));
                try {
                    ((ImageView) view.findViewById(R.id.imageViewThumb)).setImageBitmap(ThumbImage);
                } catch (Exception e) {
                    e.printStackTrace();
                }

            } catch (ParseException e) {
                e.printStackTrace();
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            }
            return view;
        }

       public Bitmap getThumbnail(ContentResolver cr, String path) throws Exception {

            Cursor ca = cr.query(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, new String[] { MediaStore.MediaColumns._ID }, MediaStore.MediaColumns.DATA + "=?", new String[] {path}, null);
            if (ca != null && ca.moveToFirst()) {
                int id = ca.getInt(ca.getColumnIndex(MediaStore.MediaColumns._ID));
                ca.close();
                return MediaStore.Images.Thumbnails.getThumbnail(cr, id, MediaStore.Images.Thumbnails.MICRO_KIND, null );
            }
            ca.close();
            return null;

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
        InputStream inputStream = getActivity().openFileInput(Const.BASE_FILE);
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

   private void showApprovalDialog() {
        new AlertDialog.Builder(getActivity())
                .setMessage(R.string.deleting_history)
                .setPositiveButton(R.string.yes, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        String fileName = Const.BASE_FILE;
                        try {
                            FileOutputStream f = getActivity().openFileOutput(fileName, Context.MODE_PRIVATE);
                            try {
                                f.close();
                            } catch (IOException e) {
                                e.printStackTrace();
                            }
                        } catch (FileNotFoundException e) {
                            e.printStackTrace();
                        }
                        for(int i = 0; i < listNames.size(); ++i) {
                            String imageFileName = listNames.get(i) + Const.JPEG_FILE_SUFFIX;
                            Log.d("img_del", imageFileName);
                            new File(imageFileName).delete();

                        }
                        //TextView tv = (TextView) findViewById(R.id.textView);
                        //tv.setVisibility(1);
                        //Button b = (Button) findViewById(R.id.button);
                        //b.setVisibility(-1);
                        list.setAdapter(null);
                    }
                })
                .setNegativeButton(R.string.no, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                    }
                })
                        //.setIcon(android.R.drawable.ic_dialog_alert)
                .show();
   }

    @Override
    public void onResume() {
        super.onResume();

    }

    @Override
    public void onPause() {
        super.onPause();
    }
}

