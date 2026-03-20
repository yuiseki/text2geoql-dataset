[out:json][timeout:30];
area["name:en"="Minato Ward"]->.outer;
area["name:en"="Nagoya"]->.inner;
(
  nwr["shop"~"bicycle"](area.inner)(area.outer);
);
out geom;
