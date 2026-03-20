[out:json][timeout:30];
area["name:en"="Midori Ward"]->.outer;
area["name:en"="Kanagawa Prefecture"]->.inner;
(
  nwr["shop"~"bicycle"](area.inner)(area.outer);
);
out geom;
