[out:json][timeout:30000];
area["name:en"="Saitama"]->.outer;
area["name:en"="Omiya Ward"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
