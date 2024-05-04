[out:json][timeout:30000];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Nakagawa Ward"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
