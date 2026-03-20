[out:json][timeout:30];
area["name:zh"="深圳市"][boundary=administrative]->.outer;
area["name:zh"="南山区"]->.inner;
(
  nwr["amenity"="fast_food"]["cuisine"="pizza"](area.inner)(area.outer);
);
out geom;
