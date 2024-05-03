[out:json][timeout:30000];
area["name:en"="Hyogo Prefecture"]->.outer;
area["name:en"="Kobe"]->.inner;
(
  nwr["shop"="convenience"]["name"~"7-Eleven"](area.inner)(area.outer);
  nwr["shop"="convenience"]["name:en"~"7-Eleven"](area.inner)(area.outer);
);
out geom;
