[out:json][timeout:30];
area["name:en"="Fukuoka Prefecture"]->.outer;
area["name:en"="Fukuoka"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;
