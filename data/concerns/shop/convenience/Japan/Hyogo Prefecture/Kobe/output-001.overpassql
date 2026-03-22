[out:json][timeout:30];
area["name:en"="Hyogo Prefecture"]->.outer;
area["name:en"="Kobe"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;