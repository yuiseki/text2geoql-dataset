[out:json][timeout:30000];
area["name:en"="Osaka"]->.outer;
area["name:en"="Yodogawa Ward"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
