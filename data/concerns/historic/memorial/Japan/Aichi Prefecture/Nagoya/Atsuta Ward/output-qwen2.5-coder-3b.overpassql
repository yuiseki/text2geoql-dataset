[out:json][timeout:30];
area["name:ja"="長野県"]->.outer;
area["name:ja"="長野市"]->.inner;
(
  nwr["memorial"](area.inner)(area.outer);
);
out geom;
