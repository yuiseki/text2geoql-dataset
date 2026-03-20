[out:json][timeout:30];
area["name:ja"="神奈川県"][boundary=administrative]->.outer;
area["name:ja"="神奈川県"]->.inner;
(
  nwr["tourism"="hostel"](area.inner)(area.outer);
);
out geom;
