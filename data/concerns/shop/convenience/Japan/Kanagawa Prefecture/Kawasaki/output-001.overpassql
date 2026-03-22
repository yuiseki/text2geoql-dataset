[out:json][timeout:30];
area["name:en"="Kanagawa Prefecture"]->.outer;
area["name:en"="Kawasaki"]->.inner;
(
  nwr["shop"="convenience"](area.inner)(area.outer);
);
out geom;