[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Ikuno Ward"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
