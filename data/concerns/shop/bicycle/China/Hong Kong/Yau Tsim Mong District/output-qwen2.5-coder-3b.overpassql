[out:json][timeout:30];
area["name:en"="Yau Tsim Mong District"]->.outer;
(
  nwr["shop"~"bicycle"](area.outer);
);
out geom;
