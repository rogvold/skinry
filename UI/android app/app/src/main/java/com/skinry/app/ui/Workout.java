package com.skinry.app.ui;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.flurry.android.FlurryAgent;
import com.skinry.app.R;

// TODO: Auto-generated Javadoc
/**
 * The Class Workout is a Fragment that is displayed in the Main activity when
 * the user taps on Workouts tab or when user swipes to third page in ViewPager.
 * You can customize this fragment's contents as per your need.
 */
public class Workout extends Fragment
{
	/* (non-Javadoc)
	 * @see android.support.v4.app.Fragment#onCreateView(android.view.LayoutInflater, android.view.ViewGroup, android.os.Bundle)
	 */

    View vv = null;

	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState)
	{
		View v = inflater.inflate(R.layout.activity_about, null);
        vv = v;
        setupView();

		return v;
	}

    private void setupView() {

        View sw = vv.findViewById(R.id.imageViewFB);
        sw.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {
                FlurryAgent.logEvent("FB_CLICKED");
                onClickFB(v);
            }
        });
        View sw1 = vv.findViewById(R.id.imageViewVK);
        sw1.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {
                FlurryAgent.logEvent("VK_CLICKED");
                onClickVK(v);
            }
        });
        View sw2 = vv.findViewById(R.id.imageViewT);
        sw2.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {
                FlurryAgent.logEvent("TMBLR_CLICKED");
                onClickTmb(v);
            }
        });

        View sw3 = vv.findViewById(R.id.rate_us_button);
        sw3.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {
                FlurryAgent.logEvent("RATE_US_CLICKED");
                btnRateAppOnClick(v);
            }
        });
    }

    /**
	 * Setup the view components for this fragment. You can write your code for
	 * initializing the views, setting the adapters, touch and click listeners
	 * etc.
	 * 
	 * @param v
	 *            the base view of fragment
	 */


	/* (non-Javadoc)
	 * @see android.view.View.OnClickListener#onClick(android.view.View)
	 */

    public void onClickFB(View v)
    {
        Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse("https://www.facebook.com/skinry"));
        startActivity(browserIntent);
    }

    public void onClickVK(View v)
    {
        Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse("https://vk.com/skinry"));
        startActivity(browserIntent);
    }

    public void onClickTmb(View v)
    {
        Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse("http://blog.skinry.com/"));
        startActivity(browserIntent);
    }

    private boolean MyStartActivity(Intent aIntent) {
        try
        {
            startActivity(aIntent);
            return true;
        }
        catch (ActivityNotFoundException e)
        {
            return false;
        }
    }

    //On click event for rate this app button
    public void btnRateAppOnClick(View v) {
        Intent intent = new Intent(Intent.ACTION_VIEW);
        //Try Google play
        intent.setData(Uri.parse("market://details?id=com.skinry.app"));
        if (!MyStartActivity(intent)) {
            //Market (Google play) app seems not installed, let's try to open a webbrowser
            intent.setData(Uri.parse("https://play.google.com/store/apps/details?id=com.skinry.app"));
            if (!MyStartActivity(intent)) {
                //Well if this also fails, we have run out of options, inform the user.

            }
        }
    }
}
