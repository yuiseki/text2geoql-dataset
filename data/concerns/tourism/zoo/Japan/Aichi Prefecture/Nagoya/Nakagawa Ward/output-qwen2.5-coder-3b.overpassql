[out:json][timeout:30];
area["name:ja"="愛知県"]->.outer;
area["name:ja"="名古屋市"]->.inner;
(
  nwr["tourism"="zoo"](area.inner)(area.outer);
);
out geom;
