[out:json][timeout:30];
area["name:ja"="日本"][boundary=administrative]->.outer;
area["name:ja"="埼玉県"]->.inner;
(
  nwr["tourism"="hostel"](area.inner)(area.outer);
);
out geom;
